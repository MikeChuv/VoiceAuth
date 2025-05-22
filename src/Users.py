from UserAccount import UserAccount


class Users(dict):
    r'''Users storage class -- `dict{ str : UserAccount}`'''
    
    def hasAccountWithLogin(self, login : str) -> bool:
        return login in self

    def __getitem__(self, __key: str) -> UserAccount:
        return super().__getitem__(__key)

    def addAccountByLogin(self, login : str) -> None:
        self[login] = UserAccount(login=login)

    def updateAccount(self, old : UserAccount, new : UserAccount) -> None:
        self[old.login] = new

    