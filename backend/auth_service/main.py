# From blueprint:python_log_in_with_replit integration
from app import app
import routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)