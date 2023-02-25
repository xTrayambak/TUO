#!/usr/bin/env python3

import os
import pathlib
import argparse
import sys

DEFAULT_MEM = 1500

# TO DEVELOPERS: MAKE SURE TO CHANGE THIS AS THE VERSION INCREASES, THIS IS NECESSARY SO THE CLIENT CAN LOCATE IT'S PROPER WORKING DIRECTORY.
VERSION = "0.1.6-dev4"


class GameHandler:
    """
    The entire backbone class of the TUO instance -- patches the game for different systems, installs required libraries, and acts as an intermediary between
    the TUO class and the raw CLI arguments.
    """

    def __init__(
        self,
        max_mem: int = DEFAULT_MEM,
        token: str = None,
        disable_gc: int = 0,
        disable_logging: int = 0,
        disable_mod_lvm: int = 0,
        gc_routine_delay: int = 120,
        debug_mode: bool = False,
        do_self_destruct: bool = None,
    ):
        from src.libinstaller import install_all_libraries, install_nim_packages
        from src.libtraceback import log_traceback
        from src.log import log, set_enabled

        log(f"PVM Environment: [{sys.executable}]")
        import gc

        if disable_gc == 0:
            gc.enable()
        else:
            gc.disable()

        set_enabled(disable_logging)

        self.debug_mode = debug_mode

        if os.path.exists("LAUNCHER_ENVIRONMENT"):
            entire_path = str(pathlib.Path(__file__))
            client_path = ""

            log(f"Full path to client startup file is [{entire_path}]")

            for dir_name in entire_path.split("/"):
                client_path += dir_name + "/"
                if dir_name == VERSION:
                    break

            """if sys.platform == 'linux':
                log("Setting client data path to ["+client_path+"]", "ClientPathDEBUG")
                os.chdir(client_path)
                log("Client working directory patch completed!", "ClientDirectoryWorkaround")"""

        log(
            "Trying to find any libraries that need to be installed.",
            "Worker/Bootstrap",
        )

        install_all_libraries()

        if debug_mode:
            log("Library installation process complete.", "Worker/Bootstrap")
            log(
                "Pre-bootup client initialization complete, now changing into client mode."
            )
            from src.client import TUO
            from src.client.gcroutine import GC

            log("Changed into client mode. Now, the client code is going to be run.")

            self.tuo = TUO(
                max_mem, token, disable_mod_lvm, self.debug_mode, do_self_destruct
            )

            if disable_gc == 0:
                gc_module = GC(self, self.tuo)
                gc_module.set_delay(gc_routine_delay)
                self.tuo.add_module(gc_module)

            self.tuo.enableParticles()
            self.run()
        else:
            try:
                from src.client.gcroutine import GC

                log("Library installation process complete.", "Worker/Bootstrap")
                log(
                    "Pre-bootup client initialization complete, now changing into client mode."
                )
                from src.client import TUO

                log(
                    "Changed into client mode. Now, the client code is going to be run."
                )
                self.tuo = TUO(
                    max_mem, token, disable_mod_lvm, self.debug_mode, do_self_destruct
                )

                if disable_gc == 0:
                    gc_module = GC(self, self.tuo)
                    gc_module.set_delay(gc_routine_delay)
                    self.tuo.add_module(gc_module)

                self.tuo.enableParticles()
                self.run()
            except Exception as exc:
                log(f"An error occured whilst initializing the game. [{exc}]")
                log_traceback()

                exit(1)

    def get_instance(self):
        """
        Get the current running instance of TUO.
        """
        return self.tuo

    def run(self):
        """
        GameHandler.run() -> self.tuo.run()
                          -> self.tuo.start_internal_game()

        ===== CONVENIENCE FUNCTION TO START A GAME INSTANCE =====
        """
        from src.libtraceback import log_traceback
        from src.log import log, warn

        if self.debug_mode:
            warn("The Untold Odyssey: DEBUG MODE")
            self.get_instance().start_internal_game()
            self.get_instance().workspace.init(self.tuo)
            self.get_instance().run()
        else:
            try:
                self.get_instance().start_internal_game()
                self.get_instance().workspace.init(self.tuo)
                self.get_instance().run()
            except Exception as e:
                log(
                    f"Caught exception whilst running game: {str(e)}", "GameHandler/Run"
                )
                log_traceback(self.tuo)
                exit(1)

        exit(0)


if __name__ == "__main__":
    mem_max = None
    token = None

    argparser = argparse.ArgumentParser(description='Run "The Untold Odyssey" client.')
    argparser.add_argument(
        "--gc",
        metavar="-g",
        type=int,
        help="Whether or not to perform manual GC routines and to also disable the automatic GC schedule of the interpreter.",
        action="store",
        required=False,
        default=0,
    )
    argparser.add_argument(
        "--token",
        metavar="-t",
        type=str,
        help="The Syntax Studios account token.",
        action="store",
        required=False,
    )
    argparser.add_argument(
        "--log",
        metavar="-l",
        type=int,
        help="Whether or not to use logging (default = 0/yes)",
        action="store",
        required=False,
        default=0,
    )
    argparser.add_argument(
        "--lvm",
        "--m",
        type=int,
        help="Whether or not to enable the modding API (default = 0/yes)",
        action="store",
        required=False,
        default=0,
    )
    argparser.add_argument(
        "--gc-delay",
        "-gcd",
        type=float,
        help="The delay at which the GC routine runs (default = 120)",
        action="store",
        required=False,
        default=120,
    )
    argparser.add_argument(
        "--debug-mode",
        "-d",
        help="Launch the game in debug mode (warning: this may disable features that make the game more unstable and unsecure, only recommended for developers/techies/nerds)",
        action="store_true",
    )

    argparser.add_argument(
        "--install-nim-libs",
        help="Launch the game, run Nimble, then quit.",
        action="store_true",
    )

    argparser.add_argument(
        "--self-destruct",
        help="Launch the game and exit immediately, only useful for benchmarking.",
        action="store_true",
    )

    args = argparser.parse_args()

    disable_gc = args.gc
    token = args.token
    disable_logging = args.log
    disable_mod_lvm = args.lvm
    gc_routine_delay = args.gc_delay
    debug_mode = args.debug_mode
    install_nim_libs = args.install_nim_libs
    self_destruct = args.self_destruct

    if install_nim_libs:
        from src.libinstaller import install_nim_packages

        install_nim_packages()
        print(
            "The Untold Odyssey: \n--install-nim-libs run, now exiting.\nYou may run the game now."
        )
        exit(0)

    if not isinstance(mem_max, int):
        mem_max = DEFAULT_MEM

    if not isinstance(token, str):
        token = "no-tok-provided"

    game = GameHandler(
        mem_max,
        token,
        disable_gc,
        disable_logging,
        disable_mod_lvm,
        gc_routine_delay,
        debug_mode,
        self_destruct,
    )
