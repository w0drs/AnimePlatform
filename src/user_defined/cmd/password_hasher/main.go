package main

import (
	"fmt"
	"kuronami/internal/core/security"
	"os"
)

func main() {
	switch len(os.Args) {
	case 1:
		withoutParameter()
		return
	case 3:
		switch os.Args[1] {
		case "-p", "-password", "-pass", "--password", "--p", "--pass":
			withTrueParameter()
			return
		default:
			tryHelp()
			return
		}
	case 2:
		switch os.Args[1] {
		case "-h", "-help", "--h", "--help":
			help()
			return
		default:
			tryHelp()
			return
		}
	default:
		tryHelp()
		return
	}
}

func withTrueParameter() {
	var password string
	password = os.Args[1]
	hash, err := security.Hash(password)
	if err != nil {
		fmt.Println("Ошибка хеширования:", err.Error())
		return
	}

	fmt.Println("Ваш захешированный пароль: ", hash)
	return
}

func withoutParameter() {
	fmt.Println("Вы попали в утилиту хеширования пароля в bcrypt")
	fmt.Println("Введите ваш пароль, который нужно захешировать:")
	var password string
	_, err := fmt.Scan(&password)
	if err != nil {
		if err.Error() != "EOF" {
			fmt.Println("Непредвиденная ошибка:", err.Error())
			return
		}
		fmt.Println("EOF: конец ввода")
		return
	}
	hash, err := security.Hash(password)
	if err != nil {
		fmt.Println("Ошибка хеширования:", err.Error())
		return
	}

	fmt.Println("Ваш захешированный пароль: ", hash)
}

func help() {
	fmt.Println("Возможные сценарии работы утилиты:")
	fmt.Println("1) main.go -p {пароль} - с параметром -p (password) и через пробел пароль на хеширование")
	fmt.Println("2) main.go - без параметров, потребует ввести пароль в консоли.")
	fmt.Println("Удачи в использовании ^_^")
}

func tryHelp() {
	fmt.Println("invalid args")
	fmt.Println("check util with --help arg.")
}
