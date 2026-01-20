
# Контроль действий

## 1. continue  
**Алиасы:** `continue`  
**Действие:** `control_skip_iteration`  
Перейти к следующей итерации цикла (`while` / `for`).  
```ts
for i in range(10):
    if (i == 5):
        continue   // пропустить 5
```

---

## 2. break  
**Алиасы:** `break`  
**Действие:** `control_stop_repeat`  
Прервать текущий цикл.  
```ts
while True:
    break
```

---

## 3. return  
**Алиасы:** `return`  
**Действие:** `control_return_function`  
Выйти из функции и вернуть значения (если указаны).  
```ts
def name():
    return
```

---

## 4. exit / stop  
**Алиасы:** `exit`, `stop`  
**Действие:** `control_end_thread`  
Остановить выполнение текущего потока скрипта.  
```ts
event player_join:
    exit
```

---

## 5. wait / sleep  
**Алиасы:** `wait`, `sleep`  
**Действие:** `control_wait`  
Приостановить выполнение на заданное время.  

| Аргумент | Тип   | Описание |
|----------|-------|----------|
| duration | number | сколько ждать |
| time_unit | enum | `TICKS`, `SECONDS`, `MINUTES` |

```ts
wait(20, "TICKS")
sleep(1.5)
```

---

## 6. error  
**Алиасы:** `error`  
**Действие:** `control_call_exception`  
Сгенерировать пользовательское исключение.  

| Аргумент | Тип  | Описание |
|----------|------|----------|
| id | text | короткий код ошибки |
| message | text | человеко-читаемое описание |
| type | enum | `ERROR`, `FATAL`, `WARNING` |

```ts
error("EMPTY_INV", "Инвентарь пуст", "FATAL")
```
