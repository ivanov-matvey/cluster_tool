from .test1 import remote_workflow, local_workflow


def main() -> None:
    while True:
        print(
            "\n=== Выберите режим работы ===\n"
            "  1 — Подключиться по SSH (удалённо)\n"
            "  2 — Локально (на этой машине)\n"
            "  0 — Выход"
        )
        mode = input("Ваш выбор: ").strip()

        if mode == "1":
            remote_workflow()
        elif mode == "2":
            local_workflow()
        elif mode == "0":
            print("До свидания!")
            break
        else:
            print("Некорректный ввод. Попробуйте снова.\n")

if __name__ == "__main__":
    main()
