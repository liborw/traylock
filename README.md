# TrayLock

Simple python automatic locking with systray icon, which can be used to deactivate it.

## Dependencies

 - [pystray](https://github.com/moses-palmer/pystray)
 - [xprintidle](https://github.com/g0hl1n/xprintidle)

## Usage

Put `trylock` command in yout autostart script.

```sh
traylock
```

## Configuration

Configuration is done through json file `.config/traylock/traylock.conf` with the following parameters:

 - `lock_cmd`: command to lock the screen.
 - `size`: size of the icon in pixels.
 - `pad`: space left on the sides of the icon.
 - `line_width`: line widh of the icon.
 - `color_bg`: color of the icon background.
 - `color_fg`: color of the icon foreground.
 - `color_90`: color of the 90% of the idle timer.
 - `color_10`: color of the last 10% of the idle timer.
 - `max_idle_time_s`: max idle time in seconds.
 - `period_s`: icon update period.

