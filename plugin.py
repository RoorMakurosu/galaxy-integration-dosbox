import sys

import os
import subprocess
import struct
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from os import listdir, environ

from dataclasses import dataclass

from urllib.parse import parse_qs, urlparse

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Game, LicenseInfo, LicenseType, Authentication, LocalGame, NextStep
from galaxy.api.consts import Platform, LocalGameState

roms_path = ""


class AuthenticationHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if "setpath" in self.path:
            self._set_headers()
            parse_result = urlparse(self.path)
            params = parse_qs(parse_result.query)
            global roms_path
            roms_path = params['path'][0]
            self.wfile.write("<script>window.location=\"/end\";</script>".encode("utf8"))
            return

        self._set_headers()
        self.wfile.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dosbox Integration</title>
            <link href="https://fonts.googleapis.com/css?family=Lato:300&display=swap" rel="stylesheet"> 
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.5/css/bulma.min.css" integrity="sha256-vK3UTo/8wHbaUn+dTQD0X6dzidqc5l7gczvH+Bnowwk=" crossorigin="anonymous" />
            <style>
                @charset "UTF-8";
                html, body {
                    padding: 0;
                    margin: 0;
                    border: 0;
                    background: rgb(40, 39, 42) !important;
                }
                
                html {
                    font-size: 12px;
                    line-height: 1.5;
                    font-family: 'Lato', sans-serif;
                }

                html {
                    overflow: scroll;
                    overflow-x: hidden;
                }
                ::-webkit-scrollbar {
                    width: 0px;
                    background: transparent;
                }

                .header {
                    background: rgb(46, 45, 48);
                    height: 66px;
                    line-height: 66px;
                    font-weight: 600;
                    text-align: center;
                    vertical-align: middle;
                    padding: 0;
                    margin: 0;
                    border: 0;
                    font-size: 16px;
                    box-sizing: border-box;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
                    color: white !important;
                }
                
                .sub-container {
                    width: 90%;
                    min-width: 200px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                Dosbox Plugin Configuration
            </div>
            
            <br />
            
            <div class="sub-container container">
                <form method="GET" action="/setpath">
                    <div class="field">
                      <label class="label has-text-light">Games Location</label>
                      <div class="control">
                        <input class="input" name="path" type="text" class="has-text-light" placeholder="Enter absolute path">
                      </div>
                    </div>
                    
                    <div class="field is-grouped">
                      <div class="control">
                        <input type="submit" class="button is-link" value="Enable Plugin" />
                      </div>
                    </div>
                </form>
            </div>
        </body>
        </html>
        """.encode('utf8'))


class AuthenticationServer(threading.Thread):
    def __init__(self, port = 0):
        super().__init__()
        self.path = ""
        server_address = ('localhost', port)
        self.httpd = HTTPServer(server_address, AuthenticationHandler)
        self.port = self.httpd.server_port

    def run(self):
        self.httpd.serve_forever()


class DosboxPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.AtariJaguar, "0.1", reader, writer, token)
        self.games = []
        self.server = AuthenticationServer()
        self.server.start()

    def parse_games(self):
        self.games = get_games(roms_path)

    def shutdown(self):
        self.server.httpd.shutdown()

    async def launch_game(self, game_id):
        from os.path import join
        for game in self.games:
            if game.program_id == game_id:
                modpath = "%%localappdata%%\\GOG.com\\Galaxy\\plugins\\installed\\atarijaguar_c1236e5a-5f3a-4681-942a-746433f255ff\\dosziplaunch.exe"
                subprocess.Popen([modpath, game.path])
                break
        return

    def finish_login(self):
        some_dict = dict()
        some_dict["roms_path"] = roms_path
        self.store_credentials(some_dict)

        self.parse_games()
        return Authentication(user_id="a_high_quality_dosbox_user", user_name=roms_path)

    async def authenticate(self, stored_credentials=None):
        global roms_path
        if len(roms_path) == 0 and stored_credentials is not None and "roms_path" in stored_credentials:
            roms_path = stored_credentials["roms_path"]

        if len(roms_path) == 0:
            PARAMS = {
                "window_title": "Configure Dosbox Plugin",
                "window_width": 400,
                "window_height": 300,
                "start_uri": "http://localhost:" + str(self.server.port),
                "end_uri_regex": ".*/end.*"
            }
            return NextStep("web_session", PARAMS)

        return self.finish_login()

    async def pass_login_credentials(self, step, credentials, cookies):
        return self.finish_login()

    async def get_owned_games(self):
        owned_games = []
        for game in self.games:
            license_info = LicenseInfo(LicenseType.OtherUserLicense, None)
            owned_games.append(Game(game_id=game.program_id, game_title=game.game_title, dlcs=None, license_info=license_info))

        return owned_games

    async def get_local_games(self):
        local_games = []
        for game in self.games:
            local_game = LocalGame(game.program_id, LocalGameState.Installed)
            local_games.append(local_game)
        return local_games


@dataclass
class NCCHGame():
    program_id: str
    game_title: str
    path: str


def probe_game(path):
    title = os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()

    title = title.replace("~", "-")

    if ext != ".dosbox" and ext != ".zip" and ext != ".DOSBOX" and ext != ".ZIP":
        return None

    title = os.path.splitext(title)[0]
    title = title.replace(".zip","")
    title = title.replace(".ZIP","")
    title = title.replace(".dosbox","")
    title = title.replace(".DOSBOX","")
    title = title.replace("  "," ")

    b = 0;
    for a in title:
        b = (b*2) + int(ord(a))

    program_id=str(b)

    return NCCHGame(program_id=program_id, game_title=title, path=path)


def get_files_in_dir(path):
    from os.path import isfile, join
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]


def get_games(path):
    games = []
    allpaths = path.split(";")
    for onepath in allpaths:
        games_path = get_files_in_dir(onepath)
        for game_path in games_path:
            game = probe_game(game_path)
            if game is not None:
                games.append(game)
    return games


def main():
    create_and_run_plugin(DosboxPlugin, sys.argv)


if __name__ == "__main__":
    main()
