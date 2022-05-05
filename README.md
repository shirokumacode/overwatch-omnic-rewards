## OWL Season 2022
This app may error out when the new season arrives. I am sure Blizzard will definately change something which will break this app. Depending on the complexity of the change I will patch this Day 1 or at the worst during the week. 

# Overwatch Omnic Rewards
[![Windows Build](https://github.com/shirokumacode/overwatch-omnic-rewards/actions/workflows/windows_build.yml/badge.svg)](https://github.com/shirokumacode/overwatch-omnic-rewards/actions/workflows/windows_build.yml)
[![Linux Build](https://github.com/shirokumacode/overwatch-omnic-rewards/actions/workflows/linux_build.yml/badge.svg)](https://github.com/shirokumacode/overwatch-omnic-rewards/actions/workflows/linux_build.yml) 
[![MacOS Build](https://github.com/shirokumacode/overwatch-omnic-rewards/actions/workflows/macos_build.yml/badge.svg)](https://github.com/shirokumacode/overwatch-omnic-rewards/actions/workflows/macos_build.yml) 

A **System Tray** app designed to **help** players **earn Overwatch League tokens** and **Contenders skins**. Cross-platform (Windows/Linux/MacOS). Created using Python and PyQt5. 



## Features
- Earn **OWL tokens and OWC skins** in the **background**
- **No Login Required**
- **Very lightweight**, doesn't inflate Youtube views 
- Uses the same mechanism as OWL/OWC website (Small colored dot)
- **Stats** - Show Hours watched/tokens earned (also csv file)
- Can **Shutdown computer** after stream ended 
- Open current stream with middle mouse click on icon (customizable left/middle click with set actions)

![](images/merged.png)


## Table of Contents

- [Install](#install)
- [FAQ](#faq)
- [How to run](#how-to-run)
- [Developing](#developing)
    - [Testing the app](#testing-the-app)
    - [Debugging the app](#debugging-the-app)
    - [Building/package the app](#buildingpackage-the-app)
- [Common Problems/Additional Questions](#common-problemsadditional-questions)

## Install

Check the [releases section](https://github.com/shirokumacode/overwatch-omnic-rewards/releases/) for Windows/Linux/MacOS executables.

Can't be sure that the MacOS executable works (never used/don't have a MacOS). Open an issue if it doesn't, and I'll fix whatever is wrong. Last resort, MacOS users should check out the [How to run](#how-to-run) section to run the app.

## FAQ
<details>
<summary>How does it work?</summary>
The app checks every 10min if OWL/OWC is currently live. If it's live, it will start to "watch" and track watch time. It uses the same mechanism as the OWL/OWC website to track your watch time.
</details>

<details>
<summary>What does it need?</summary>
No logins, no passwords. It only needs your Blizzard user_id that you can obtain in <5secs. Follow the steps on the app to get it. 
</details>

<details>
<summary>Does it work?</summary>
It does. I've tested the mechanism for the past month. I haven't open the OWL/OWC website so far and earned all the tokens and June OWC skins.

This mechanism was already found and implemented before (with minor differences). See these repositories:
- [cyandterry/OWL-Token](https://github.com/cyandterry/OWL-Token)
- [TrebuchKill/owl-token-guide](https://github.com/TrebuchKill/owl-token-guide)
</details>

<details>
<summary>Is it more reliable than the website?</summary>
It is as you don't rely on the youtube player status (playing/not playing) to track. Also you can have ad-blockers blocking the necessary tracking endpoints. However I can't guarantee the OWL tracking endpoints are stable (sometimes they go down). 
</details>

<details>
<summary>Won't this get detected/broken?</summary>
This app behaves like a normal browser/user and should be undetectable.
I reverse engineered the mechanism that is used to track the user on OWL/OWC site. The mechanism itself is very simple. 

If the devs change the mechanism, it should be possible to patch the app fairly easily. Can't guarantee it will work forever. 
</details>

<details>
<summary>I am a developer. Can I see this method/code?</summary>
You should check out the utils folder and the examples inside. Any python programmer should be able to see what it does in <5min. Feel free to use/reimplement. 
</details>

<details>
<summary>Can you make this app run at startup/login/boot?</summary>
You certainly can. Just download the executable and follow the steps below

- [Windows guide](https://support.microsoft.com/en-us/windows/add-an-app-to-run-automatically-at-startup-in-windows-10-150da165-dcd9-7230-517b-cf3c295d89dd)
- Linux - depends on the distribution/DE
    - [KDE](https://userbase.kde.org/System_Settings/Autostart)
    - [Arch](https://wiki.archlinux.org/title/autostarting#On_desktop_environment_startup)
</details>
    
**Any doubts on how it all works** or if you want more specifics, **open a discussion** and I'll try to explain everything with the best of my abilities.

Also if you **want any features/changes**, **open a discussion** and I'll try to implement it if feasable. If you can code you can also PR it

## How to Run

Run the executables from the [releases section](https://github.com/shirokumacode/overwatch-omnic-rewards/releases/)

OR

1. Clone the repository 
2. Install Python (3.9 recommended) and then pipenv
```shell
pip install pipenv
```
3. Run the app under pipenv environment
```shell
pipenv install
pipenv run python app.py
```

## Developing

This app uses pipenv to manage its requirements. Install the dev requirements if you want to develop and test the app
```shell
pipenv install --dev
```
and then start a shell to get to the virtual env and then run the app.
```shell
pipenv shell
python app.py
```

(Optional) You can compile your own pyqt resource file. I already provide it for ease of use but you should make sure the code is right.
```shell
pyrcc5 resources.qrc -o resources_qc.py
```

### Testing the app
Given that the OWL/OWC isn't always live it is unfeasible to test the app. I created a simple flask server to mock the requests - test/flaskapi.py
```shell
cd test/
python flaskapi.py
```
You can comment/uncomment certain lines to get the desired behaviour you want to mimic or even change how many minutes you want to fake "watch".

To run the app using local endpoints
```shell
python app.py --debug
```

### Debugging the app
Run the app with verbose mode (logging level: info)
```shell
python app.py -v
```
You can also set the logging level (info, warning, debug)
```shell
python app.py -l <logging level>
```

If you need to get the logs in a file format with a timestamp (_\<filename\>_ is optional, defaults to _omnic.log_)
```shell
python app.py --file-log <filename>
```
### Building/package the app
Run PyInstaller
- Linux build
```shell
pyinstaller app.py -n omnic_rewards_Linux --onefile 
```
- Windows build
```shell
pyinstaller app.py -n omnic_rewards_Windows -w -i icons\iconowl.ico --onefile 
```

### Code/PR away and feel free to criticize my code. I would really like to **get real advice** as it was my first time using PyQt.

## Common Problems/Additional Questions

Any bugs/problems that are **not covered** by these questions, please **open an issue** 

<details>
<summary>The app is displaying errors</summary>
The app should tell you what the problem is. Make sure your account is set and you are connected to the Internet. 

If you get a notification as well it needs user intervention. Use the check now button/action to see if it clears. 
</details>

<details>
<summary>Getting "Watcher Bad API Response"</summary>
It is probably the tracking endpoints having a breakdown. When people complain the circle is disappearing on the website it's this error.
</details>

<details>
<summary>"OWC/OWC seems Live, not tracking" - Getting 0min watched warning</summary>
When the stream ends, the OWL website takes a while to remove the live now panel. The app detects it is "live" but it can't track/"watch". This is most likely the reason. 
</details>

<details>
<summary>My app dissappeared</summary>
That indicates a hard crash. Try to reproduce it and open a issue on Github so I can fix it.
</details>

<details>
<summary>My PC didn't shutdown after the stream ended</summary>
The app tries to shutdown the computer on the next false live check.

- Linux: Depends on *systemctl*
- Windows: Not tested but should work
- MacOS: Can't test if the method used to shutdown works at all (open issue on Github if it doesn't)
</details>

<details>
<summary>My problem isn't listed here</summary>
Open an issue on Github so I can try to fix it
</details>

<details>
<summary>Can I change the time between checks?</summary>
You can via Settings->Experimental or manually changing the config file (config.json) but you might get 0min watched warnings (at the end of a stream) if it's too low. I feel 10min (default) is a good compromise.
</details>

<details>
<summary>Can I run this with multiple accounts?</summary>
You can. To do this you should

- Place the app in different folders with different config files (config.json) for each account

OR
- Create multiple config files and run the app multiple times using the --config argument (CLI mode is also recommended to eliminate the multiple system tray icons -> --cli argument)
```shell
python app.py --config config1.json
python app.py --config config2.json
```
</details>

<details>
<summary>Can I get my watch history with more detail?</summary>
The app creates a csv file with your watch history. Check the created file - history.csv
</details>

<details>
<summary>Can I run this without the system tray icon or on a server?</summary>
You can using the CLI mode. The argument -c or --cli makes the system tray not visible, and runs exclusively on the command line.

```shell
python app.py --cli
```
Also this mode doesn't require any graphical dependencies so you can run it on a server without a display. This mode assumes that you already have a config.json with accountid field (copy one created previously and change it accordingly or create a json file with the accountid field).
</details>

<details>
<summary>This app is really good. Can I hire you?</summary>
My resume consists of 4999SR Genji main with coding on the side. I accept food as payment. Email me
</details>


Contact me/Open a discussion for further explanations or anything else not explained here






