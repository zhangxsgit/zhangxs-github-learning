import sys
if sys.version_info < (3,0,0):                # Python2 / Python3 difference
	from COM_parser          import COMparser
	from ui_main_frame       import Hauptfenster
	from ui_com_frame        import COMfenster
	from mmi                 import mmi
	from config              import config
	from diagram             import diagram
else:
	from mylib.COM_parser    import COMparser
	from mylib.ui_main_frame import Hauptfenster
	from mylib.ui_com_frame  import COMfenster
	from mylib.mmi           import mmi
	from mylib.config        import config
	from mylib.diagram       import diagram
