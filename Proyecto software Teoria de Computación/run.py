
from flask import Flask
from app.controllers.rule_controller import rule_bp

app = Flask(
    __name__,
    template_folder="app/views/templates",
    static_folder="app/views/static"
)

app.register_blueprint(rule_bp)

if __name__ == "__main__":
    app.run(debug=True)
