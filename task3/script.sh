#!/bin/bash

# Проверка на наличие аргумента
if [ -z "$1" ]; then
  echo "Usage: $0 <flagstat_output_file>"
  exit 1
fi

file="$1"

# Извлечение строки с процентом mapped
percent=$(grep "mapped (" "$file" | sed -E 's/.*\(([^%]+)%.*/\1/')

# Проверка, удалось ли извлечь число
if [ -z "$percent" ]; then
  echo "Could not extract mapped percentage"
  exit 2
fi

# Вывод процента
echo "Mapped: $percent%"

# Проверка условия
percent_int=$(echo "$percent > 90" | bc)

if [ "$percent_int" -eq 1 ]; then
  echo "OK"
else
  echo "NOT OK"
fi

