# Backup_25160 inspection

Uploaded archive: `Backup_25160.tar`.

## What it contains

This archive is a SA-MP/CRMP server backup, not Android launcher source code.

Detected structure:

- `server.cfg`
- `samp03svr`
- `samp-npc`
- `plugins/`
- `gamemodes/redex.amx`
- `include/` and `pawno/include/`
- `scriptfiles/redex_server_settings.ini`
- `scriptfiles/redex_mysql_settings.ini`
- `backup_database/database.sql`
- server/mysql logs

## Server config summary

Redacted summary from `server.cfg`:

- bind IP: `80.242.59.112`
- port: `3585`
- gamemode: `redex`
- maxplayers: `50`
- query: enabled
- announce: enabled
- plugins include: `crashdetect`, `mysql_static`, `pawnraknet`, `pawncmd`, `profiler`, `sscanf`, `streamer`, `sampvoice`, `tutor`, `pawn_json`

Redacted summary from `redex_server_settings.ini`:

- nameserver: `KABAN RUSSIA`
- whitelist: `0`
- default money/vip/lvl values are present

## Sensitive data warning

Do not upload this full TAR to a public repository.

The backup contains sensitive material:

- RCON password in `server.cfg`
- MySQL host/user/password/database in `redex_mysql_settings.ini`
- full SQL database backup
- server logs

Recommended actions:

1. Rotate/change the RCON password.
2. Rotate/change the MySQL password.
3. Do not commit `database.sql` publicly.
4. Add `.gitignore` rules for database dumps, logs and secret INI files.

## Android launcher relevance

This backup does not contain:

- Android Studio/Gradle project source
- original APK signing keystore
- `.jks` / `.keystore` file
- original signed APK source project

So this archive cannot solve the APK update-signature problem by itself.

However, it does provide the game server address that the launcher/server-list data should point to:

```text
80.242.59.112:3585
```

The inspected launcher APK contains external data endpoints such as:

- `https://api-free.crmp.pro/`
- `https://api-free.crmp.pro/client/`
- `https://fastdl.ragerussia.online/`
- a Dropbox `servers.json` URL

If the launcher says it cannot connect to the data server, the next real fix is not the SA-MP server itself. The next real fix is to provide or patch the launcher data/config endpoint so it returns a server list containing `KABAN RUSSIA` at `80.242.59.112:3585`.

## Recommended next step

Create a clean hosted launcher config endpoint, for example:

```text
https://your-domain.example/servers.json
```

Then patch the APK to use that endpoint instead of the old Dropbox `servers.json` URL.

The JSON schema still needs to match what the APK expects. From static inspection, the launcher has a `Server` model with fields:

- `ip`
- `port`
- `name`
- `firstName`
- `secondName`
- `color`
- `online`
- `maxOnline`
- `key`
- `url`
- `x2`
- `x2cordx`
- `x2cordy`
- `testServerId`

Before making a final APK, test the config endpoint response with the installed app logs.
