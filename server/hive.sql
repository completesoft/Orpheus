-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u2
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Апр 13 2017 г., 11:33
-- Версия сервера: 5.5.53-0+deb8u1
-- Версия PHP: 5.6.27-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- База данных: `hive`
--

-- --------------------------------------------------------

--
-- Структура таблицы `counter_events`
--

CREATE TABLE IF NOT EXISTS `counter_events` (
  `drone_id` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `counter_event_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `counter_values`
--

CREATE TABLE IF NOT EXISTS `counter_values` (
  `drone_id` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `visitors` int(11) NOT NULL,
  `temperature` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `drones`
--

CREATE TABLE IF NOT EXISTS `drones` (
`id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `type` int(11) NOT NULL,
  `description` varchar(100) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `drones`
--

INSERT INTO `drones` (`id`, `name`, `type`, `description`) VALUES
(11, 'vs-dekabristov', 1, 'Декабристов Видеосервер'),
(77, 'test-client', 0, ''),
(78, 'test2', 0, ''),
(79, 'test3', 0, ''),
(80, 'test4', 0, ''),
(81, 'test5', 0, ''),
(82, 'test50', 0, '');

-- --------------------------------------------------------

--
-- Структура таблицы `events`
--

CREATE TABLE IF NOT EXISTS `events` (
  `serverdatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `drone_id` int(10) unsigned NOT NULL,
  `drone_timestamp` datetime NOT NULL,
  `event_id` int(10) unsigned NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `events`
--

INSERT INTO `events` (`serverdatetime`, `drone_id`, `drone_timestamp`, `event_id`) VALUES
('2017-03-05 22:18:38', 1, '1970-01-01 03:00:00', 2),
('2017-04-13 11:33:38', 11, '1970-01-01 03:00:00', 2),
('2017-04-05 20:18:47', 82, '2017-04-05 23:18:46', 1);

-- --------------------------------------------------------

--
-- Структура таблицы `orpheus_inserts`
--

CREATE TABLE IF NOT EXISTS `orpheus_inserts` (
  `drone_id` int(11) NOT NULL,
  `insert_time` time NOT NULL,
  `description` varchar(100) NOT NULL,
  `url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `orpheus_mainstream`
--

CREATE TABLE IF NOT EXISTS `orpheus_mainstream` (
  `drone_id` int(11) NOT NULL,
  `mainstream_url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `orpheus_mainstream`
--

INSERT INTO `orpheus_mainstream` (`drone_id`, `mainstream_url`) VALUES
(11, 'http://ic3.101.ru:8000/c2_1');

-- --------------------------------------------------------

--
-- Структура таблицы `orpheus_silents`
--

CREATE TABLE IF NOT EXISTS `orpheus_silents` (
  `drone_id` int(11) NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `description` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `orpheus_states`
--

CREATE TABLE IF NOT EXISTS `orpheus_states` (
  `drone_id` int(11) NOT NULL,
  `state` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `orpheus_states`
--

INSERT INTO `orpheus_states` (`drone_id`, `state`) VALUES
(1, 'play'),
(11, 'play');

-- --------------------------------------------------------

--
-- Структура таблицы `software`
--

CREATE TABLE IF NOT EXISTS `software` (
  `name` varchar(100) NOT NULL,
  `description` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `version` int(10) unsigned NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `software`
--

INSERT INTO `software` (`name`, `description`, `url`, `version`) VALUES
('akm', 'Рабочее место кассира', '', 2017022001),
('clientdisplay', 'Экран покупателя', '', 2017022001),
('dnepr_kvint_r', 'Розница Днепровская', '', 2017022001),
('m_client', 'Клиент системы сообщений', '', 2017022001),
('test', 'Тестовая программа', 'http://update.product.in.ua/new/test/test_update.zip', 2017021901),
('updater', 'Клиентский модуль обновления', 'http://update.product.in.ua/new/updater2/client.zip', 2017022001),
('zaktt', 'Модуль заказа магазина', '', 2017022001),
('zavod_kvint_o', 'Основная Заводская', '', 2017022001);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `counter_events`
--
ALTER TABLE `counter_events`
 ADD PRIMARY KEY (`drone_id`,`time`,`counter_event_id`);

--
-- Индексы таблицы `counter_values`
--
ALTER TABLE `counter_values`
 ADD PRIMARY KEY (`drone_id`,`time`);

--
-- Индексы таблицы `drones`
--
ALTER TABLE `drones`
 ADD PRIMARY KEY (`id`), ADD UNIQUE KEY `id` (`id`);

--
-- Индексы таблицы `events`
--
ALTER TABLE `events`
 ADD PRIMARY KEY (`drone_id`,`event_id`);

--
-- Индексы таблицы `orpheus_inserts`
--
ALTER TABLE `orpheus_inserts`
 ADD PRIMARY KEY (`drone_id`,`insert_time`);

--
-- Индексы таблицы `orpheus_mainstream`
--
ALTER TABLE `orpheus_mainstream`
 ADD PRIMARY KEY (`drone_id`), ADD UNIQUE KEY `drone_id` (`drone_id`);

--
-- Индексы таблицы `orpheus_silents`
--
ALTER TABLE `orpheus_silents`
 ADD PRIMARY KEY (`drone_id`,`start_time`,`end_time`);

--
-- Индексы таблицы `orpheus_states`
--
ALTER TABLE `orpheus_states`
 ADD PRIMARY KEY (`drone_id`);

--
-- Индексы таблицы `software`
--
ALTER TABLE `software`
 ADD PRIMARY KEY (`name`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `drones`
--
ALTER TABLE `drones`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=83;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
