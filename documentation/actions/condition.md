# Условия

## Базовая форма

```
if условие:
    блок
else if условие:
    блок
elif условие:
    блок
else:
    блок
```

Блоки **обязательно** с отступом (таб / 4 пробела).  
`else if`/`elif` можно писать сколько угодно раз; `else` — не более одного и только в конце.

---

## Использование

Заместо `if(player::is_flying())` как в jmcc, здесь нужно писать `if player.is_flying() либо if player(is_flying())`.
То есть просто выносите player, entity, world, variable за скобку.
Если же вы ничего не укажите: `if ()`, то это активирует режим кастомных условий:

```ts
event player_join:
    if (num == 1):
    if num != 1:
    if (num > 9):       
    if (num >= 9):             
    if num < 9:            
    if num <= 9:                 

    // строковые проверки
    if text.contains("hello"):             
    if (username.startswith("Mr","Mrs","Dr")): 
    if (filename.endswith(".txt",".log")):

    // переменные
    if myVar.exists():

    // Если есть в списке/словаре
    if l`player` in list(g`myList`)
    if l`player` in dict(g`myDict`)
```

## Отрицание

Поставьте `not` или `!` сразу после if:

```ts
if not player.is_sneaking():
if !player(is_flying())):
```
