from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_pod():
    request_info = request.get_json()
    uid = request_info["request"]["uid"]
    pod_spec = request_info["request"]["object"]["spec"]
    
    containers = pod_spec.get("containers", [])
    
    for container in containers:
        image = container.get("image", "")
        security_context = container.get("securityContext", {})
        
        # 🚨 الشرط الأول: منع الـ Root
        if security_context.get("runAsUser") == 0 or not security_context.get("runAsNonRoot", False):
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": False,
                    "status": {"message": "🚨 Security Blocked: Container is attempting to run as ROOT! This is forbidden."}
                }
            })
            
        # 🚨 الشرط الثاني: منع المستودعات غير الموثوقة
        trusted_registry = "mycompany.azurecr.io"
        if not image.startswith(trusted_registry):
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": False,
                    "status": {"message": f"🚨 Security Blocked: Image '{image}' is from an untrusted registry! Only '{trusted_registry}' is allowed."}
                }
            })

    return jsonify({
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {"uid": uid, "allowed": True}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, ssl_context=('cert.crt', 'key.key'))
