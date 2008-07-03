

from wtforms import HiddenField


class IdField(HiddenField):

    def _value(self):
	    return self.data and unicode(self.data) or u'0'

    def process_formdata(self, valuelist):
        try:
            self.data = int(valuelist[0])
            if self.data == 0:
                self.data = None
        except ValueError:
            self.data = None

