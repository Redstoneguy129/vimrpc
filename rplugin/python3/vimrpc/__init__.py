from .pidlock import PidLock, get_tempdir
from os.path import basename, join
import neovim
import os

DEBUG_MODE = os.getenv("SSH_CONNECTION") is None
if DEBUG_MODE:
    with open("../../../vimrpc.json", 'r') as config_file:
        config = json.load(config_file)
else:
    with open(os.path.join(vim.eval('s:plugin_root_dir'), '..', '..', '..', 'vimrpc.json'), 'r') as config_file:
        config = json.load(config_file)
has_thumbnail = '_'.join([item['name'] for item in config['languages']]).split('_')
has_thumbnail.pop()


@contextmanager
def handle_lock(plugin):
    try:
        yield
    except NoDiscordClientError:
        plugin.locked = True
        plugin.log_warning("local vimrpc client not found")
    except ReconnectError:
        plugin.locked = True
        plugin.log_error("ran out of reconnect attempts")


@neovim.plugin
class VimRPCPlugin(object):
    def __init__(self, vim):
        self.vim = vim
        self.activate = self.vim.vars.get("vimrpc_activate_on_enter")
        self.activity = {}
        self.discord = None
        self.blacklist = []
        self.fts_blacklist = []
        self.fts_whitelist = []
        self.project_url = None
        self.lock = None
        self.locked = False
        self.lastfilename = None
        self.lastused = False
        self.lasttimestamp = int(time())
        self.cbtimer = None

    @neovim.autocmd("VimEnter", "*", sync=True)
    def on_vimenter(self):
        self.blacklist = []

    @neovim.autocmd("BufEnter", "*", sync=True)
    def on_bufenter(self):
        if self.activate != 0:
            self.update_presence()

    @neovim.command("DiscordUpdatePresence")
    def update_presence(self):
        if self.activate == 0:
            self.activate = 1
        if not self.activity:
            self.activity = "vim"
        if not self.lock:
            self.lock = PidLock(join(get_tempdir(), "dnvim_lock"))
        if self.locked:
            return
        if not self.discord:
            reconnect_threshold =  self.vim.vars.get("vimrpc_reconnect_threshold")
            self.locked = not self.lock.lock()
            if self.locked:
                self.log_warning("pidfile exists")
                return
            self.discord = Discord(reconnect_threshold)
            with handle_lock(self):
                self.discord.connect()
                self.log_debug("init")
            if self.locked:
                return
            atexit.register(self.shutdown)
        ro = self.get_current_buf_var("&ro")
        if ro:
            return
        filename = self.vim.current.buffer.name
        if not filename:
            return
        self.log_debug('filename: {}'.format(filename))
        ft = self.get_current_buf_var("&ft")
        self.log_debug('ft: {}'.format(ft))
        if ft not in has_thumbnail:
            return
        workspace = self.get_workspace()
        if self.is_ratelimited(filename):
            if self.cbtimer:
                self.vim.call("timer_stop", self.cbtimer)
            self.cbtimer = self.vim.call("timer_start", 15, "_DiscordRunScheduled")
            return
        self.log_debug("update presence")
        with handle_lock(self):
            self._update_presence(filename, ft, workspace)

    def _update_presence(self, filename, ft, workspace):
        self.discord.update(ft, workspace+"/"+basename(filename))

    def get_current_buf_var(self, var):
        return self.vim.call("getbufvar", self.vim.current.buffer.number, var)

    def get_workspace(self):
        bufnr = self.vim.current.buffer.number
        dirpath = self.vim.call("vimrpc#GetProjectDir", bufnr)
        if dirpath:
            return basename(dirpath)
        return None

    @neovim.function("_DiscordRunScheduled")
    def run_scheduled(self, args):
        self.cbtimer = None
        self.update_presence()

    def is_ratelimited(self, filename):
        if self.lastfilename == filename:
            return True
        now = int(time())
        if (now - self.lasttimestamp) >= 15:
            self.lastused = False
            self.lasttimestamp = now
        if self.lastused:
            return True
        self.lastused = True
        self.lastfilename = filename

    def log_debug(self, message, trace=None):
        self.vim.call("vimrpc#LogDebug", message, trace)

    def log_warning(self, message, trace=None):
        self.vim.call("vimrpc#LogWarn", message, trace)

    def log_error(self, message, trace=None):
        self.vim.call("vimrpc#LogError", message, trace)

    def shutdown(self):
        self.lock.unlock()
        self.discord.disconnect()