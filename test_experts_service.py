from backend.app.services.experts_service import get_experts

experts = get_experts()

print("TOTAL PEOPLE FOUND:", len(experts))

for expert in experts[:15]:
    print("\nNAME:", expert["name"])
    print("ROLES:", expert["roles"])
    print("EVIDENCE COUNT:", expert["evidence_count"])

    if expert["evidence"]:
        print("SOURCE:", expert["evidence"][0])