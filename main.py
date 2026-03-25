from app import create_app
import sys, traceback

def loud_excepthook(exc_type, exc_value, exc_tb):
    print("\n" + "="*80)
    print("UNCAUGHT EXCEPTION:")
    traceback.print_exception(exc_type, exc_value, exc_tb)
    print("="*80 + "\n")

sys.excepthook = loud_excepthook

app = create_app()

if __name__ == "__main__":
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["TRAP_HTTP_EXCEPTIONS"] = True
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["DEBUG"] = True
    app.run(host="0.0.0.0", port=5000, debug=True)