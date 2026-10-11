
from flask import Blueprint, render_template, request, jsonify
from app.models.rule import Rule
from app.services.rule_analyzer import analyze_rule

rule_bp = Blueprint("rules", __name__)


@rule_bp.route("/")
def index():
    return render_template("index.html")


@rule_bp.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    try:
        rule = Rule.from_dict(data)
        result = analyze_rule(rule.source)
        return jsonify(result.to_dict())

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
