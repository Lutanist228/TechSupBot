class DataStorage:
    objects: dict = {}

    def erase_objects(user_id: int):
        keys: list = list(DataStorage.objects.keys())
        keys_copy = keys.copy()
        
        try:
            for object in keys_copy:
                object: str
                user_id = str(user_id)
                if user_id in object:
                    DataStorage.objects.pop(object)
                    # print(f"Пользовательский объект {object} был успешно удален из памяти хранилища")
                else:
                    pass
                    # print(f"Пользовательский объект {object} не найдет в памяти хранилища. Ниже представлено содержимое хранилища:\n\n{DataStorage.objects}")
        except RuntimeError as err:
            # print(f"Объект {object} не был удален из памяти хранилища по причине ошибки:\n\n{err}")
            pass
        


