import esp
import uos
import gc

esp.osdebug(None)
gc.collect()

import webrepl
webrepl.start()
