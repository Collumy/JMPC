# Кастомные условия

Кастомные действия — это лаконичные «однострочные» конструкции, которые компилятор разворачивает в обычные внутренние вызовы.

Синтаксис: ключевое слово области + двоеточие + выражение.

| Ключевое слово | Область | Пример |
|----------------|---------|--------|
| `list` / `l` | списки | `list: a = []` |
| `map` / `dict` / `d` | словари | `dict: prices = {}` |
| `text` / `t` | текст | `text: greeting = "Hello" + name` |
| `number` / `num` / `n` | числа | `num: sum = 1 + 2 + 3 + 4` |
| `assign` | мультиприсваивание | `assign: \n a = 2 \n b = 3` |

---

## 1. Списки 

| Задача | Синтаксис(ы) |
|--------|--------------|
| создать | `list = []` |
| добавить | `list = list.append(val)` / `list.add(val)` |
| объединить | `list = list.merge(list2)` / `list.extend(list2)` / `list = list1 + list2` / `list1 += list2` |
| установить по индексу | `list[index] = val` / `list = list.set(index, val)` |
| вставить | `list = list.insert(val)` / `list.ins(val)` |
| случайное значение | `val = list.get_random()` / `list.random()` / `list.rand()` |
| получить | `val = list[index]` / `list.get(index)` / `list.value(index)` |
| получить индекс значения | `index = list.index(val)` |
| удалить значения | `list = list.delete_values(val)` / `del_values` / `del_val` |
| удалить по индексу | `list = list.delete_index(i)` / `del_index` / `del_ind` |
| удалить повторы | `list = list.delete_repeats()` / `del_repeats` / `del_rep` |
| обрезка / срез | `list = list[0:5]` / `list[:3]` / `list[-2:]` / `list.cut(from, to)` / `list.slice(from, to)` |
| перевернуть | `list = list.reverse()` / `list.rev()` / `list[::-1]` |
| размер | `list.size()` / `list.length()` / `list.len()` / `len(list)` |
| сортировать | `list = list.sort()` |
| рандомизировать | `list = list.randomize()` |
| сгладить | `list = list.smooth()` |

---

## 2. Словари 

| Задача | Синтаксис(ы) |
|--------|--------------|
| создать | `dict = {}` |
| из списков ключ-знач | `dict.list(keys, vals)` / `dict.by_list(keys, vals)` |
| объединить | `dict = dict1 + dict2` / `dict1.merge(dict2)` / `dict1.extend(dict2)` |
| установить | `dict[key] = val` / `dict.set([key1, val1], [key2, val2], …)` |
| получить значение | `val = dict[key]` / `dict.get(key, default)` / `dict.value(key, default)` |
| получить по индексу | `val = dict.index(key, default)` |
| размер | `dict.size()` / `dict.length()` / `dict.len()` / `len(dict)` |
| удалить ключ | `dict = dict.delete(key, val)` / `dict.del(key, val)` |
| очистить | `dict.clear()` |
| список ключей | `list = dict.keys()` |
| список значений | `list = dict.values()` |
| ключ по значению | `key = dict.key_by_value(val, marker)` / `key_by_val` |
| ключ по индексу | `key = dict.key_by_index(i)` / `key_by_ind` |
| сортировать | `list = list.sort(order, type)` |

---

## 3. Текст 

| Задача | Синтаксис(ы) |
|--------|--------------|
| объединить | `result = text.join("a", "b", "c")` / `text.concat` / `text.merge` |
| заменить | `result = text.replace("old", "new")` |
| удалить | `text.remove("bad")` / `delete` / `del` / `remove("regex", "TRUE")` |
| обрезка | `text.slice(from, to)` / `substring(from)` / `substr(from, len)` / `trim(from?, to?)` |
| регистр | `upper()` / `lower()` / `to_case(...)` |
| повторить | `"str".repeat(n)` / `"str" * n` |
| список → строка | `list.join_list(", ", "[", "]")` / `implode(", ")` |
| очистить цвета | `text.clear_colors()` / `strip_colors()` / `no_colors()` |
| символ по индексу | `char = text.char_at(i)` / `get_char(i)` / `char(i)` |
| код символа | `code = char.ord()` / `char_code()` / `ascii()` |
| символ из кода | `char = text.chr(65)` / `from_char_code(64)` / `from_ascii(97)` |
| длина | `text.len()` / `length()` / `size()` |
| разделить | `list = text.split(",")` / `explode(";")` |

---

## 4. Числа (Number)

| Задача | Синтаксис(ы) |
|--------|--------------|
| арифметика | `+` `-` `*` `/` `%` `++` `--` |
| комбинированное | `+=` `-=` `*=` `/=` `%=` `^=` |
| степень | `a ^ b` |
| функции | `abs(x)` `min(a,b,c…)` `max(a,b,c…)` `clamp(x,min,max)` |
| округление | `round(x)` `round(x, 2)` `floor(x)` `ceil(x)` |
| логарифм | `log(x, base)` |
| случайные | `random(min, max)` `randint(min, max)` |
