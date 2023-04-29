from sklearn.base import TransformerMixin


class JobDuty(TransformerMixin):
    def __init__(self):
        pass

    def fit(self, store):
        print("enter jobduty fit,pars=")
        return self

    def transform(self, store):
        print("enter jobduty transform")
        return store
