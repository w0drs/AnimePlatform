package main

import (
	"fmt"
	"kuronami/internal/core/security"
)

func main() {
	fmt.Println("Вы попали в утилиту хеширования пароля в bcrypt")
	fmt.Println("Введите ваш пароль, который нужно захешировать:")
	var password string
	_, err := fmt.Scan(&password)
	if err != nil {
		fmt.Println("Непредвиденная ошибка:", err.Error())
		return
	}
	hash, err := security.Hash(password)
	if err != nil {
		fmt.Println("Ошибка хеширования:", err.Error())
		return
	}

	fmt.Println("Ваш захешированный пароль: ", hash)
}
