# MiCtl - Управление роутером Mikrotik RB941

Автоматизирует рутинную операцию смены локального IP-адреса роутера и связанных параметров (DNS, DHCP).

Цель проекта - максимально ускорить процесс интеграции роутера в сеть в ситуациях, когда роутер часто 
переносится из одной сети в другую.

### Алгоритм работы
- Запрашивает адрес интерфейса у пользователя. Остальные параметры заданы в тексте программы.
- Проверяет введённые данные на консистентность (диапазон DHCP должен быть в сети роутера)
- Запрашивает пароль для подключения у пользователя.
- Устанавливает параметры DHCP сервера по образцу
  - /ip dhcp-server network set address=192.168.1.0/24 netmask=24 gateway=192.168.1.250 dns-server=192.168.1.250 0
- Устанавливает параметры DHCP пула по образцу
  - /ip dhcp-server set address-pool=dhcp 0
  - /ip pool set dhcp ranges=192.168.1.220-192.168.1.248
- Устанавливает параметры DNS
  - /ip dns static set name=router.lan address=192.168.1.250 0
- Устанавливает адрес роутера
  - /ip address set address=192.168.1.250/24 interface=bridge 0
  
 ### Известные проблемы
 
 - Подвержена проблеме https:/github.com/ktbyers/netmiko/issues/3405
