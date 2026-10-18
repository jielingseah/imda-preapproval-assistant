"""
Assessment Schemas for IMDA Pre-Approval Assistant.
Centralized Single Source of Truth for corporate, deployment, and solution baseline criteria.
"""

BASELINE_PREREQUISITES_SCHEMA = {
    "corporate": [
        {
            "key": "incorporated",
            "label": "Company incorporated in Singapore",
            "question": "Is your company incorporated in Singapore?",
            "options": ["Yes", "No"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "operation",
            "label": "Operation for at least 18 months",
            "question": "Has your company been in operation for at least 18 months?",
            "options": ["Yes", "No"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "financial",
            "label": "Financial stability (positive equity & ratio >= 1)",
            "question": "Is your company financially stable (positive net equity, current ratio >= 1)?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "track_record",
            "label": "Government agency track record",
            "question": "Does your company have satisfactory track record with government agencies?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "resources",
            "label": "Sufficient quality resources",
            "question": "Does your company have sufficient quality resources?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "cooling",
            "label": "Free from 1-year IMDA cooling period",
            "question": "Is your company free from any IMDA one-year cooling period?",
            "options": ["Yes", "No"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "invoice_now",
            "label": "InvoiceNow registered account",
            "question": "Has your company signed up for an InvoiceNow account?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        }
    ],
    "deployment": [
        {
            "key": "industries",
            "label": "Industry specialization",
            "question": "Select the statement that best describes the industries your solution caters to.",
            "options": ["Many industries", "One or few industries", "Not sure"],
            "compliant_values": ["Many industries", "One or few industries"]
        },
        {
            "key": "customer_track",
            "label": "Deployed with >= 5 SG SMEs for >= 6 months",
            "question": "Has your solution been deployed with at least 5 Singapore-registered SMEs for at least 6 months?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        }
    ],
    "solution": [
        {
            "key": "pricing",
            "label": "Priced reasonably for SMEs",
            "question": "Is your solution priced reasonably for SMEs?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "suitability",
            "label": "Designed for SME needs",
            "question": "Is your solution designed to suit the needs and demands of SMEs?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "productivity",
            "label": "Improves SME productivity",
            "question": "Does your solution help SMEs improve productivity?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "website",
            "label": "Active website showcasing solution",
            "question": "Do you have a website that showcases the solution?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "dapdp",
            "label": "Data protection & analytics compliance",
            "question": "Have you validated compliance with Data Analytics and Personal Data Protection requirements?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        }
    ]
}
