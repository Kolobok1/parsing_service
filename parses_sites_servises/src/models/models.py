class CompanyInfo:
    def __init__(self):
        self.organization_id = None
        self.site = None
        self.status = 'no'
        self.confirmation = 'no'
        self.title = 'no'
        self.description = 'no'
        self.email = None
        self.yandex = 'no'
        self.google = 'no'

    def to_map(self):
        return {
            'organization_id': self.organization_id,
            'site': self.site,
            'status': self.status,
            'confirmation': self.confirmation,
            'title': self.title,
            'description': self.description,
            'email': self.email,
            'yandex': self.yandex,
            'google': self.google
        }
