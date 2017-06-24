from books.conf.settings import ACC_CHOICES, CURRENCIES, ACTIONS

def initial_account_types():
	"""Makes sure all of the initial account types exist."""
	from books.models import AccountType

	#Create all the default account types if they don't exist already
	existing_types = AccountType.objects.all()
	for acc_choice in ACC_CHOICES:
	    choice = acc_choice[1]
	    choice_found = False

	    for t in existing_types:
	        if t.name == choice:
	            choice_found = True

	    if not choice_found:
	        AccountType.objects.create(name = choice)