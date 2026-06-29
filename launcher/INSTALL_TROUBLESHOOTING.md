# Если APK пишет «Приложение не установлено»

## Самая вероятная причина

Патч `KABAN_RUSSIA_16.26.7.1_patched_debugsigned.apk` сохранил старый package:

- `com.break.russia`

Но APK был переподписан debug-ключом. Если на телефоне уже стоит старая версия `com.break.russia`, подписанная другим ключом, Android не даст поставить новый APK поверх неё.

Обычно это выглядит как:

- `Приложение не установлено`
- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`
- `Package signatures do not match`

## Что можно сделать

### Вариант 1. Удалить старое приложение

Удалить установленный старый лаунчер и поставить debug APK заново.

Минус: могут потеряться локальные данные приложения.

### Вариант 2. Подписать оригинальным keystore

Это лучший вариант для настоящего обновления поверх старой версии.

Нужен старый keystore, которым был подписан оригинальный APK. Без него Android считает новый APK чужим приложением, даже если package name тот же.

### Вариант 3. Тестовая сборка рядом со старой

Для проверки UI и базового запуска можно сделать side-test сборку с другим package:

- original package: `com.break.russia`
- side-test package: `com.break.rusdev`

Такой APK должен ставиться рядом со старым приложением и не конфликтовать по подписи.

Важно: side-test package может иметь ограничения из-за Firebase/AppMetrica/Billing/server config, потому что часть сервисов может ожидать оригинальный package.

## Что было сделано для side-test APK

В manifest заменены package/authorities/permissions с префиксом:

- `com.break.russia` → `com.break.rusdev`
- `com.break.russia.firebaseinitprovider` → `com.break.rusdev.firebaseinitprovider`
- `com.break.russia.provider` → `com.break.rusdev.provider`
- `com.break.russia.androidx-startup` → `com.break.rusdev.androidx-startup`

Также app label в ресурсах изменён:

- `KABAN RUSSIA` → `KABAN DEBUG `

## Важное правило для релиза

Для настоящего релизного APK нужно одно из двух:

1. найти оригинальный keystore;
2. выпускать приложение как новое, с другим package, и делать миграцию для игроков.

Иначе Android не позволит обновить старое приложение поверх установленного.
