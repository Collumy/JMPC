# Контроллер
---

## 1. async_run / async  
**Алиасы:** `async_run`, `async`  
**Действие:** `controller_async_run`  
Выполнить тело **в отдельном потоке** (не блокирует основной).  

```ts
controller async():
    wait(5)
    player::message("Асинхронное сообщение!")
```

---

## 2. do_not_run / skip  
**Алиасы:** `do_not_run`, `skip`  
**Действие:** `controller_do_not_run`  
Полностью **исключает** тело из скрипта (удобно для временного отключения).  

```ts
controller skip():
    list = []   // никогда не выполнится
```

---

## 3. exception / catch_error / catch  
**Алиасы:** `exception`, `catch_error`, `catch`  
**Действие:** `controller_exception`  

| Аргумент | Тип     | Описание |
|----------|---------|----------|
| variable | variable | переменная, куда запишется объект ошибки |

```ts
controller catch(err):
    n: num--
player::message("Ошибка: ${err.message}")
```

---

## 4. measure_time / time / measure  
**Алиасы:** `measure_time`, `time`, `measure`  
**Действие:** `controller_measure_time`  

| Аргумент | Тип  | Описание |
|----------|------|----------|
| variable | variable | куда сохранить результат |
| duration | enum | единица измерения: `NANOSECONDS`, `MICROSECONDS`, `MILLISECONDS` |

```ts
controller measure(t, MILLISECONDS):
    wait(1)
player::message("Выполнено за ${t} мс")
```
