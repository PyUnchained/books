import os

from django.db.utils import IntegrityError
from django.db.models import Q
from django.conf import settings

from openpyxl import load_workbook

from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS

def migrate_to_single_entry():
    from books.models import JournalEntry, SingleEntry, Account, AccountGroup
    SingleEntry.objects.all().delete()
    tot = 0
    info = [["debit Feed (Hay & Pellets)", "credit Cash", 19.5, "abbe92a3-360d-4af5-8906-11726d7212b1"], ["debit Cash", "credit Capital", 2919.62, "66124eff-64c2-4e8b-bcf6-c214faa618b7"], ["debit Feed (Hay & Pellets)", "credit Cash", 19.5, "fbc3683a-5ed9-4431-9794-5d339864ec98"], ["debit Buildings", "credit Cash", 5.4, "5ec45160-3003-4742-9d35-ee140fce746e"], ["debit Buildings", "credit Cash", 38.45, "c2d24d2e-bcc2-4e55-b2fc-16bbdeda8104"], ["debit Buildings", "credit Cash", 16.75, "77c078f9-8da1-44e6-a540-2e12b3a91a34"], ["debit Veterenary & Sanitation", "credit Cash", 21.0, "b77f9fbb-d6d5-4619-bc1a-4162564289ae"], ["debit Buildings", "credit Cash", 46.8, "26af631b-876c-4d48-a3a1-31ea95059fcc"], ["debit Feed (Hay & Pellets)", "credit Cash", 30.0, "92ea1a63-ed9a-4ba4-be76-b51042c2816a"], ["debit Buildings", "credit Cash", 50.55, "db3f3c31-1b94-437a-a30e-badbd26b77b4"], ["debit Buildings", "credit Cash", 33.63, "997cf6e5-73c2-45d8-8372-6769de4b4ece"], ["debit Buildings", "credit Cash", 4.56, "c1076108-f80a-4210-9763-f3223f472d7a"], ["debit Feed (Hay & Pellets)", "credit Cash", 4.25, "127cc50b-593e-470e-bfa1-c74b560a00b9"], ["debit Buildings", "credit Cash", 81.65, "2a872f7b-226c-418c-869b-6bc2ad68e6d0"], ["debit Feed (Hay & Pellets)", "credit Cash", 28.0, "4fbd1d18-4b7a-4e29-b6fb-8123b756d541"], ["debit Buildings", "credit Cash", 20.38, "9d49a838-5eed-4958-a6bd-ecb9aa34d9c6"], ["debit Buildings", "credit Cash", 1.25, "eacf0b2f-7d17-4d8e-92aa-f541e32542ed"], ["debit Buildings", "credit Cash", 107.0, "7e4fc3eb-3030-4e7a-95c2-5efe93bbe2af"], ["debit Buildings", "credit Cash", 4.91, "ea83124a-47e8-4bf3-8f87-8ec20f2fbf6e"], ["debit Buildings", "credit Cash", 4.2, "14a31b9e-f987-4e81-bbc3-7f06caf8edcb"], ["debit Buildings", "credit Cash", 27.22, "6ad2cdd7-f3dc-41c2-a103-17791dec132a"], ["debit Buildings", "credit Cash", 20.0, "8cde5fc8-a6e2-4bfd-8e9c-1ebc2a79d850"], ["debit Buildings", "credit Cash", 1.4, "932b1d72-ca6c-42c4-8293-4cdfae4d9076"], ["debit Feed (Hay & Pellets)", "credit Cash", 59.4, "f9df6f7a-f2b3-4544-a373-8b1357a62f33"], ["debit Furniture and Fixtures", "credit Cash", 28.0, "aa4558a7-6366-49ef-baff-9443157395f7"], ["debit Feed (Hay & Pellets)", "credit Cash", 29.0, "d5266827-b3aa-4740-a759-c66061b791e8"], ["debit Feed (Hay & Pellets)", "credit Cash", 59.4, "e4cb541e-c1ee-4ae0-90d7-df6478aefd01"], ["debit Buildings", "credit Cash", 31.57, "07ed1c91-cb65-4052-8835-dd7f7c660e62"], ["debit Veterenary & Sanitation", "credit Cash", 9.0, "a2090804-4196-4d5b-bdf0-f2440b7e4e62"], ["debit Veterenary & Sanitation", "credit Cash", 14.0, "b4f29922-6fac-47da-88ea-53cb25a28f7f"], ["debit Buildings", "credit Cash", 81.0, "9346dd59-968b-4cea-bea0-27822b1823c2"], ["debit Buildings", "credit Cash", 14.16, "4a070a62-58ff-44f0-944f-ced773e27bc2"], ["debit Veterenary & Sanitation", "credit Cash", 10.0, "85e4ef85-d3af-4259-ba72-1c7df71e9b5a"], ["debit Buildings", "credit Cash", 97.85, "b17886ac-0951-4f46-b5ab-0bf902fdf88a"], ["debit Veterenary & Sanitation", "credit Cash", 38.0, "62d0acc2-86ef-4ace-9826-bcd181252cfc"], ["debit Veterenary & Sanitation", "credit Cash", 38.0, "a3715c09-0358-4172-8cb4-950352f3b803"], ["debit Buildings", "credit Cash", 119.5, "7849bc33-8e2d-4440-8f98-fbad233e763a"], ["debit Veterenary & Sanitation", "credit Cash", 3.0, "1be9b509-5738-4e8b-ac6a-762303b43784"], ["debit Buildings", "credit Cash", 55.5, "314fa708-dc4a-4963-82f2-cfd21a7e1bac"], ["debit Buildings", "credit Cash", 25.0, "675e118b-cef6-4d9e-a184-bea3fb6606ba"], ["debit Veterenary & Sanitation", "credit Cash", 7.0, "f500c9dc-a18b-4966-b544-5f62cc64111c"], ["debit Buildings", "credit Cash", 10.0, "24755efa-26d7-4cad-84a6-28aa29560487"], ["debit Buildings", "credit Cash", 10.0, "df8470d5-46d9-4c5a-8de7-f11808e2c3db"], ["debit Buildings", "credit Cash", 83.15, "c8394afc-2b2b-4c6f-8db6-47b510e489c4"], ["debit Buildings", "credit Cash", 23.9, "50d7443b-6627-4438-9f0f-de1c231be86c"], ["debit Buildings", "credit Cash", 10.0, "62dd708f-bf78-4247-8fdc-5f89de826848"], ["debit Veterenary & Sanitation", "credit Cash", 17.1, "afc9d89a-c42d-4b90-8815-3d35a3107adb"], ["debit Feed (Hay & Pellets)", "credit Cash", 59.5, "7470589f-2b69-46e2-8fad-385a0e5e6ac7"], ["debit Veterenary & Sanitation", "credit Cash", 10.0, "5d3d1ae2-22d9-4b14-9d60-db85a3c1e560"], ["debit Veterenary & Sanitation", "credit Cash", 21.0, "746867db-1013-4582-b9ca-b28366b4f02e"], ["debit Buildings", "credit Cash", 2.0, "c2ffff6f-c911-457c-b91b-64764f030fab"], ["debit Buildings", "credit Cash", 8.0, "7ff74b24-2ff6-44ab-ba7e-572abac0bf77"], ["debit Buildings", "credit Cash", 22.0, "1fa16746-b2c5-4b55-9ccc-a081d8d45948"], ["debit Buildings", "credit Cash", 26.0, "1242da0f-ba8d-497b-9e94-e728f5331eea"], ["debit Veterenary & Sanitation", "credit Cash", 2.6, "9c729f24-519d-45b4-8c71-3968fee3d9d2"], ["debit Feed (Hay & Pellets)", "credit Cash", 59.5, "7d4ff707-b4ee-446a-a014-8db7f5007ec9"], ["debit Buildings", "credit Cash", 10.0, "d0beb9e9-f654-4ecf-9b7a-cc2e7fb0858a"], ["debit Veterenary & Sanitation", "credit Cash", 54.75, "04e83367-8d25-4477-932b-3f7f7b216d85"], ["debit Buildings", "credit Cash", 25.0, "a13c157a-3a3e-4bad-b9d8-ce78e0fdc462"], ["debit Feed (Hay & Pellets)", "credit Cash", 64.5, "88bd936e-080c-417e-b718-8b11e26acf37"], ["debit Veterenary & Sanitation", "credit Cash", 60.5, "d0a24781-e58c-40dd-ae97-b76862a4e5dd"], ["debit Buildings", "credit Cash", 2.0, "960fbae0-f608-4e6e-8f02-e3d4963d980a"], ["debit Buildings", "credit Cash", 16.63, "275dfe90-59c1-40c8-aba0-4340159f2c48"], ["debit Feed (Hay & Pellets)", "credit Cash", 29.0, "9238038e-5726-4af5-86f9-25e8cc8d7981"], ["debit Buildings", "credit Cash", 266.0, "009bdbd8-efde-4302-97eb-9f621f5a26f1"], ["debit Buildings", "credit Cash", 18.4, "44ce395f-0a1d-4e6d-a3d0-4fbf4a631dfe"], ["debit Buildings", "credit Cash", 2.0, "5eebc139-c1bf-489d-8c07-1f5e32c643d6"], ["debit Veterenary & Sanitation", "credit Cash", 10.0, "f7f53d58-9730-4d0e-9fc8-3faa8601e40b"], ["debit Buildings", "credit Cash", 31.76, "544a39bc-c4f7-42a3-abf2-78cfb7bfbe59"], ["debit Veterenary & Sanitation", "credit Cash", 46.78, "e502d925-69bc-475f-843c-55916b92c6f1"], ["debit Buildings", "credit Cash", 0.3, "40b7e7d8-dca1-4204-8709-9dbadf792cf8"], ["debit Buildings", "credit Cash", 42.14, "e6130413-1a07-4236-a89e-86bb97e86029"], ["debit Feed (Hay & Pellets)", "credit Cash", 64.5, "77b0c6e5-7ce9-4b51-a00c-260b21e4e3ef"], ["debit Feed (Hay & Pellets)", "credit Cash", 96.75, "eef91961-02e3-4663-be40-48b85fdaed04"], ["debit Feed (Hay & Pellets)", "credit Cash", 24.0, "29f5b848-4f30-4dc4-81a9-a573f8b06a8c"], ["debit Veterenary & Sanitation", "credit Cash", 11.0, "cabdedff-646b-4d56-9341-167f06da447d"], ["debit Veterenary & Sanitation", "credit Cash", 25.5, "20f90da1-697f-4bd7-a4eb-dba14f1894d2"], ["debit Veterenary & Sanitation", "credit Cash", 9.0, "014e0de3-96e9-4f05-a8f8-6ff34b365b30"], ["debit Feed (Hay & Pellets)", "credit Cash", 39.0, "96043dd6-14a8-4549-93db-d950106d89b9"], ["debit Feed (Hay & Pellets)", "credit Cash", 29.7, "d0960efe-4739-4cb3-8dc7-38b2ab3ca4e8"], ["debit Feed (Hay & Pellets)", "credit Cash", 44.46, "98594afc-bc89-4f3d-b2aa-6b26c82eb1b6"], ["debit Buildings", "credit Cash", 10.0, "d416d8a0-29d3-4569-8482-d6abb054da81"], ["debit Fuel and Transportation", "credit Cash", 30.0, "02810390-b0a6-4f52-b898-a15d0a15ebe2"], ["debit Buildings", "credit Cash", 5.94, "bc74be69-81fa-43db-880b-50b32cdae6f5"], ["debit Buildings", "credit Cash", 2.03, "992a7588-57c3-412c-8e69-4a5db009fb0f"], ["debit Buildings", "credit Cash", 2.75, "965e9a09-5766-447a-9dd3-04159aeddc7e"], ["debit Tools & Equipment", "credit Cash", 18.5, "fa78cb81-cbf6-49f7-abe0-681ba8b7d96a"], ["debit Buildings", "credit Cash", 60.03, "9c9088ab-115a-4465-9054-1497c9a5d54b"], ["debit Veterenary & Sanitation", "credit Cash", 5.0, "79088397-070b-47e5-8e80-64f7e24afd7f"], ["debit Buildings", "credit Cash", 8.7, "055a55df-f3cc-4ebe-aa49-a14874aa16cd"], ["debit Buildings", "credit Cash", 5.73, "63c67918-759e-45bf-b06e-fe40098fabcd"], ["debit Feed (Hay & Pellets)", "credit Cash", 59.4, "8fe6c8df-a12b-47cc-8b18-680b22169081"], ["debit Buildings", "credit Cash", 2.84, "85ad97d5-0186-4a22-a1e0-a3be4a2fed2a"], ["debit Feed (Hay & Pellets)", "credit Cash", 14.5, "3c5138f5-6aa0-40ef-b3f6-d5d8e9c940c4"]]
    for item in info:
        je = JournalEntry.objects.get(pk = item[3])
        debit_name = item[0].replace('debit ', '')
        if debit_name == 'Cash':
            debit_name = 'Petty Cash Account'
        elif 'Buildings' in debit_name:
            debit_name = 'Property'
        elif 'Furniture and Fixtures' in debit_name:
            debit_name = 'Equipment'
        elif 'Fuel and Transportation' in debit_name:
            Account.objects.get_or_create(name = 'Fuel and Transportation',
                code = 'Fuel and Transportation',
                account_type = AccountGroup.objects.get(name = 'expense')
                )
        elif 'Tools & Equipment' in debit_name:
            debit_name = 'Equipment'
        debit_acc = Account.objects.get(name = debit_name)

        credit_name = item[1].replace('credit ', '')
        if credit_name == 'Capital':
            credit_name = 'Owners Contributions'
        elif credit_name == 'Cash':
            credit_name = 'Petty Cash Account'
        credit_acc = Account.objects.get(name = credit_name)

        debit_entry = SingleEntry.objects.get_or_create(journal_entry = je,
            account = debit_acc, action = 'D', value = item[2])
        credit_entry = SingleEntry.objects.get_or_create(journal_entry = je,
            account = credit_acc, action = 'C', value = item[2])
        tot += item[2]

def initial_account_types():
    """Makes sure all of the initial account types exist."""
    from books.models import AccountGroup

    #Create all the default account types if they don't exist already
    existing_types = AccountGroup.objects.all()
    for acc_choice in ACC_CHOICES:
        choice = acc_choice[1]
        choice_found = False

        for t in existing_types:
            if t.name == choice:
                choice_found = True

        if not choice_found:
            AccountGroup.objects.create(name = choice)

def chart_of_accounts_setup():

    from django.conf import settings
    from books.models import Account, AccountGroup

    try:
        ACTIVE_BOOKS_PACKAGE = settings.ACTIVE_BOOKS_PACKAGE
    except:
        ACTIVE_BOOKS_PACKAGE = 'book_keeping'

    COA_FILE_PATH = os.path.join(settings.BASE_DIR, 'books/conf/coa.xlsx')
    coa_wb = load_workbook(COA_FILE_PATH)
    all_sub_types = []
    all_types = []
    for n, rec in enumerate(coa_wb['book_keeping']):
        if n > 0:
            parent_group, created = AccountGroup.objects.get_or_create(
                name = rec[3].value.lower())
            acc_group, acc_created = AccountGroup.objects.get_or_create(
                name =rec[4].value.lower())

            if acc_created:
                acc_group.parent = parent_group
                acc_group.save()

            account_data = {'name' : rec[0].value.title(),
            'code' : rec[1].value,
            'account_type': acc_group}

            try:
                Account.objects.get_or_create(**account_data)

            #If the code already exists, but other details
            #have been changed in the coa excel file
            except IntegrityError:
                code = account_data.pop('code')
                Account.objects.update_or_create(
                        code=code, defaults=account_data
                )
