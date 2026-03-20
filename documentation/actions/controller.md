# Контроллер

## async_run / async  
**Алиасы:** `async_run`, `async`  
**Действие:** `controller_async_run`  
Выполнить тело в отдельном потоке

```ts
controller.async():
    wait(5)
    player::message("Асинхронное сообщение!")
```

---

## do_not_run / skip  
**Алиасы:** `do_not_run`, `skip`  
**Действие:** `controller_do_not_run`  
Полностью исключает тело из скрипта

```ts
controller.skip():
    list = []   // никогда не выполнится
```

---

## exception / catch_error / catch  
**Алиасы:** `exception`, `catch_error`, `catch`  
**Действие:** `controller_exception`  
Поймать ошибку внутри блока кода

| Аргумент | Тип     | Описание |
|----------|---------|----------|
| variable | variable | переменная, куда запишется объект ошибки |

```ts
controller.catch(err):
    n: num--
player::message("Ошибка: ${err}")
```

---

## measure_time / time / measure  
**Алиасы:** `measure_time`, `time`, `measure`  
**Действие:** `controller_measure_time` 
Измерить время

| Аргумент | Тип  | Описание |
|----------|------|----------|
| variable | variable | куда сохранить результат |
| duration | enum | единица измерения: `NANOSECONDS`, `MICROSECONDS`, `MILLISECONDS` |

```ts
controller measure(t, "MILLISECONDS"):
    wait(1)
player::message("Выполнено за ${t} мс")
```
