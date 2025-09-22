# Консольное приложение для управления кластерами 1С

Инструмент для автоматизации рутинных операций администрирования платформы 1C:Enterprise из командной строки Linux или по SSH. Он оборачивает утилиту rac в набор команд высокого уровня

Стек: `Python`

Основной функционал:
- просматривать и изменять конфигурацию кластера
- создавать/удалять информационные базы
- управлять сеансами, серверами и процессами
- собирать статистику использования

<br>

## Архитектура

```
app/
 ├─ commands/  # команды верхнего уровня, связывают UI и managers
 │   ├─ cluster.py  # ClusterCommands
 │   ├─ infobase.py   # InfobaseCommands
 │   └─ ...
 ├─ executors/  # исполнители команд
 │   ├─ base.py  # базовый исполнитель (общая логика + парсеры)
 │   ├─ local.py   # исполнитель для локальных команд
 │   └─ remote.py  # исполнитель для удаленных команд по SSH
 ├─ managers/  # низкоуровневые вызовы rac
 │   ├─ cluster.py  # ClusterManager
 │   ├─ infobase.py  # InfobaseManager
 │   └─ ...
 ├─ ui/  # общие функции вывода/ввода
 ├─ config.py  # конфигурация
 └─ workflow.py  # меню
main.py  # точка входа и выбор режима

```

<br>

## Команды

Auth Params: `--cluster-user` `--cluster-pwd`

Infobase Params: `--name` `--dbms` `--db-server` `--db-name` `--locale` `--db-user` `--db-pwd` `--descr`

|                         | Пункт меню                                    | Описание                                                                  | Горячая логика (`rac ...`)                                                               |
|-------------------------|-----------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| **Кластеры**            | Список кластеров                              | Выводит список кластеров                                                  | `rac cluster list`                                                                       |
|                         | Топ по сессиям                                | Показывает топ кластеров по количеству сессий                             | `rac cluster list` `rac session list --cluster=<UUID> [auth-params]`                     |
|                         | Обновить период перезапуска рабочих процессов | Обновляет lifetime сеансов                                                | `rac cluster update --cluster=<UUID> --lifetime-limit=<сек>`                             |
| **Информационные базы** | Список информационных баз                     | Выводит список информационных баз для выбранного кластера                 | `rac infobase summary list --cluster=<UUID> [auth-params]`                               |
|                         | Информация об информационной базе             | Выводит полную информацию об информационной базе                          | `rac infobase info --cluster=<UUID> --infobase=<UUID> [auth-params]`                     |
|                         | Создать информационную базу                   | Создает информационную базу                                               | `rac infobase create --create-database [infobase-params] --cluster=<UUID> [auth-params]` |
|                         | Удалить информационную базу                   | Удаляет информационную базу                                               | `rac infobase drop --cluster=<UUID> --infobase=<UUID> [auth-params]`                     |
| **Сеансы**              | Список сеансов                                | Выводит список сеансов для выбранного кластера                            | `rac session list --cluster=<UUID> [auth-params]`                                        |
|                         | Информация о сеансе                           | Выводит полную информацию о сеансе                                        | `rac session info --session=<UUID> --cluster=<UUID> [auth-params]`                       |
|                         | Информация о лицензиях сеансов                | Выводит полную информацию о лицензиях сеанса                              | `rac session info --session=<UUID> --cluster=<UUID> --licenses [auth-params]`            |
|                         | Завершить сеанс                               | Удаляет сеанс                                                             | `rac session terminate --session=<UUID> --cluster=<UUID> [auth-params]`                  |
| **Серверы**             | Список серверов                               | Выводит полную информацию о серверах                                      | `rac server list --cluster=<UUID> [auth-params]`                                         |
|                         | Информация о сервере                          | Выводит полную информацию о рабочем сервере                               | `rac server info --cluster=<UUID> --server=<UUID> [auth-params]`                         |
| **Процессы**            | Список рабочих процессов                      | Выводит полную информацию о процессах для выбранного кластера             | `rac process list --cluster=<UUID> [auth-params]`                                        |
| **Администраторы**      | Список администраторов                        | Выводит список администраторов кластеров                                  | `rac cluster admin list --cluster=<UUID> [auth-params]`                                  |
|                         | Обновить аккаунт администратора кластеров     | Обновляет информацию об администраторе кластеров                          | Создаёт или обновляет администратора, записывая логин и зашифрованный пароль             |
| **Бонус**               | Тест множественный выбор                      | Выводит меню, в котором можно выбрать несколько пунктов, нажатием `Space` |                                                                                          |

<br>

## Быстрый старт

```bash
# 1. Клонируйте репозиторий и установите зависимости
git clone https://github.com/ivanov-matvey/cluster_tool && cd cluster_tool
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Запустите главное меню
cd ..
python -m cluster_tool
```

