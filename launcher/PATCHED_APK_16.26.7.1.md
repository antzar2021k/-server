# Patched launcher APK 16.26.7.1

Выполнена первая практическая доработка именно существующего APK из архива `Под 64.zip`.

## Исходный APK

- File: `KABAN RUSSIA (1).apk`
- Package: `com.break.russia`
- Version before: `16.26.7.0`
- VersionCode before: `1183`
- SHA-256: `16a71f8762887e5e97701547c843e467852e6d94f828cedbebd84658acf4ba6e`

## Патч

- Version after: `16.26.7.1`
- VersionCode after: `1184`
- Package preserved: `com.break.russia`
- Launcher activity preserved: `com.blackhub.bronline.launcher.activities.MainActivity`
- Game activity preserved: `com.blackhub.bronline.game.core.JNIActivity`
- Native ABI preserved: `arm64-v8a`, `armeabi-v7a`

## Видимые изменения UI-строк

- `Играть` → `ЗАПУСК`
- `Настройки` → `ПАРАМЕТРЫ`
- `Сервер` → `ОНЛАЙН`

## Что НЕ менялось

Чтобы не сломать существующий запуск и загрузку клиента, на первом патче не менялись:

- package name;
- activity names;
- permissions;
- native libraries;
- update/network flow;
- billing/Firebase/AppMetrica configs;
- `usesCleartextTraffic`;
- `requestLegacyExternalStorage`.

## Подпись

APK пересобран и подписан debug-ключом `kaban_debug`.

Важно: debug-signed APK нельзя установить как обновление поверх старого приложения, если старый APK был подписан другим ключом. Для обновления поверх установленной версии нужен оригинальный keystore или официальный механизм смены ключа в магазине.

## Patched artifact

- Debug-signed APK SHA-256: `b509afa269424662c486db12db33b0fb53d83d1ddb12e5093f0560310bbaec29`
- Unsigned APK SHA-256: `c8cafef56c1bbba9e419152b93cbd4f9f0af9d2520f2116123afeb0d280d8b8a`

## Следующие реальные доработки

1. Подменить/улучшить фон главного экрана и кнопку запуска.
2. Добавить более понятный экран ошибки обновления.
3. Переоформить прогресс загрузки.
4. Проверить HTTP/HTTPS и storage flags на тестовом устройстве.
5. Если найдётся keystore — подписать release-сборку правильным ключом.
