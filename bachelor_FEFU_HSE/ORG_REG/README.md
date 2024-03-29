## ORG_REG - это проект по созданию технического задания в виде схематичного описания сервиса (телеграм - бота) для предоставления базовых консультаций по выбору организационно-правовой формы при регистрации НКО.
### Используемые технологии: MS Word, Draw Io.

#### Проблема:
   Процедура регистрации НКО является одной из основных и непростых задач на этапе создания НКО. Она вызывает у обычного человека трудности, из-за которых он чаще всего обращается к специалисту в данной области – юристу. В первую очередь сложности возникают с выбором организационно-правовой формы (ОПФ). От выбора той или иной формы регистрации зависит весь дальнейший процесс и уже на данном этапе человек сталкивается с множеством юридических тонкостей и идет за консультацией к специалисту. 
   
   Однако, весь процесс выбора формы для юриста однообразен и включает в себя последовательное выявление нужной формы путем исключения неподходящих. Достаточно примитивный с точки зрения алгоритма процесс выбора вызывает трудности у людей, желающих зарегистрировать НКО. Данная процедура может быть автоматизирована для сокращения издержек как клиентов, так и юристов. 
   
#### Актуальность:
   Финансирование НКО со стороны государства растет с каждым годом. Действия Правительства направлены на расширение некоммерческого сектора в экономике страны. Оно поощряет создание новых НКО, и граждане активно этому способствуют. 
   
####  Пользователи:
Пользователями данной проблемы являются с одной стороны – клинеты, желающие создать НКО, а с другой стороны – юристы, которые сопутствуют клиентам в создании НКО. Для клиентов данная проблема проявляется в том, что они вынуждены обращаться за услугами специалистов уже на первоначальном этапе, поскольку для них самостоятельно определить ОПФ НКО представляется достаточно трудным в связи с юридическими тонкостями.

В свою очередь для юристов данная проблема проявляется в том, что они вынуждены тратить своё время на консультирование людей по данному вопросу (данная процедура для юристов является стандартизированой), в то время как они могли бы заниматься бумажной работой по регистрации НКО (выявление недочетов в пакете документов клиента на регистрацию НКО). Таким образом, шансы на успешную регистрацию организации клиента растут одновременно с уменьшением сроков длительности данной операции. 

#### Цели и задачи:
Целью проекта является ликвидация иррациональности в процессе выбора ОПФ НКО. Стандартизированность данного процесса позволяет поставить следующую задачу: создать сервис, оптимизирующий процесс основания НКО. Необходимо построить алгоритм, который путем последовательных вопросов и ответов на них будет приводить к одной или нескольких ОПФ, наиболее подходящим для конкретного клиента. 

#### Таким образом, процедура оптимизируется по представленной ниже схеме:

![](https://github.com/maxzhrvl/projects/blob/main/bachelor_FEFU_HSE/ORG_REG/%D0%9F%D1%80%D0%BE%D1%86%D0%B5%D1%81%D1%81%20%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8.png)

#### Сервис (телеграм-бот) предполагает стартовое меню (приветственное сообщение, уточнение имени пользователя) из которого осуществляется переход в меню выбора основных функций бота:

![](https://github.com/maxzhrvl/projects/blob/main/bachelor_FEFU_HSE/ORG_REG/%D0%A1%D1%82%D0%B0%D1%80%D1%82%D0%BE%D0%B2%D0%BE%D0%B5%20%D0%BC%D0%B5%D0%BD%D1%8E%20%D0%B1%D0%BE%D1%82%D0%B0.png)

#### Бот обладает следующим функционалом:

1. Помощь в выборе организационно-правовой формы будущей НКО:

![](https://github.com/maxzhrvl/projects/blob/main/bachelor_FEFU_HSE/ORG_REG/%D0%A4%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8F%20%E2%84%961.png)

2. Предоставление информации о базовых условиях существования различных организационно-правовых форм НКО в соответствии с законодательством:

![](https://github.com/maxzhrvl/projects/blob/main/bachelor_FEFU_HSE/ORG_REG/%D0%A4%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8F%20%E2%84%962.png)

3. Предоставление информации о мерах поддержки (финансировании) НКО:

![](https://github.com/maxzhrvl/projects/blob/main/bachelor_FEFU_HSE/ORG_REG/%D0%A4%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8F%20%E2%84%963.png)

4. Предоставление первичных указаний по сбору пакета документов для регистрации НКО в Минюсте:

![](https://github.com/maxzhrvl/projects/blob/main/bachelor_FEFU_HSE/ORG_REG/%D0%A4%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8F%20%E2%84%964.png)

#### В рамках реализации проекта удалось:
1. Выявить проблему, её актуальность, ключевых пользователей
2. Cобрать информацию по разновидностям, законодательным аспектам, мерам поддержки НКО
3. Проконсультировавшись со специалистом, составить ТЗ, содержащее перечень и механизм реализации функций сервиса, основанный на собранной информации
4. Проиллюстрировать алгоритм в виде блок-схем для упрощения дальнейшей реализации ТЗ

С отчетом по проекту Вы можете ознакомиться [здесь](https://docs.google.com/document/d/1wQ7QDSIC8VKUqazsWkU9zkUznskMVixz/edit?usp=sharing&ouid=105441550085605533821&rtpof=true&sd=true).

