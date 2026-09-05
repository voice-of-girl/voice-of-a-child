"""
Transparent Rule-Based Matching Engine for Voice of a Girl.
Evaluates beneficiary eligibility against programme and opportunity requirements
without black-box opacity. Always provides human-interpretable match reasons
and missing criteria.
"""
from typing import Dict, List, Any
from datetime import date

def calculate_match(beneficiary_profile: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes transparent rule-based score (0 - 100%)
    
    beneficiary_profile:
      - district: str
      - country: str
      - date_of_birth: date/str
      - education_level: str
      - skills: list[str]
      - interests: list[str]
      - career_goals: str
      
    requirements:
      - allowed_locations: list[str]
      - min_age: int
      - max_age: int
      - required_education: list[str]
      - desired_skills: list[str]
      - desired_interests: list[str]
    """
    score = 0
    max_possible = 100
    reasons: List[str] = []
    missing_requirements: List[str] = []

    # 1. Location Matching (25 points)
    allowed_locations = requirements.get('allowed_locations', [])
    b_district = (beneficiary_profile.get('district') or '').lower().strip()
    b_country = (beneficiary_profile.get('country') or '').lower().strip()
    
    if not allowed_locations or any(loc.lower().strip() in [b_district, b_country] for loc in allowed_locations):
        score += 25
        reasons.append(f"Location aligns: {beneficiary_profile.get('district', 'Target District')}")
    else:
        missing_requirements.append(f"Located in {beneficiary_profile.get('district')}; programme prioritises {', '.join(allowed_locations)}")

    # 2. Age Criteria (20 points)
    dob = beneficiary_profile.get('date_of_birth')
    age = None
    if dob:
        if isinstance(dob, str):
            try:
                parts = dob.split('-')
                birth_year = int(parts[0])
                current_year = date.today().year
                age = current_year - birth_year
            except Exception:
                age = 20
        elif hasattr(dob, 'year'):
            age = date.today().year - dob.year
    else:
        age = 21 # default demographic estimate

    min_age = requirements.get('min_age', 15)
    max_age = requirements.get('max_age', 30)

    if age is not None:
        if min_age <= age <= max_age:
            score += 20
            reasons.append(f"Age {age} falls directly within eligible bracket ({min_age}–{max_age} years)")
        else:
            missing_requirements.append(f"Age {age} is outside the priority bracket ({min_age}–{max_age} years)")
    else:
        score += 10 # partial if age not stated

    # 3. Education Matching (20 points)
    req_edu = requirements.get('required_education', [])
    b_edu = beneficiary_profile.get('education_level', '')
    if not req_edu or b_edu in req_edu:
        score += 20
        reasons.append(f"Education level ({b_edu}) matches programme prerequisite")
    else:
        missing_requirements.append(f"Has {b_edu}, requirement is one of {', '.join(req_edu)}")

    # 4. Skills Match (20 points)
    desired_skills = [s.lower().strip() for s in requirements.get('desired_skills', [])]
    b_skills = [s.lower().strip() for s in beneficiary_profile.get('skills', [])]
    
    if desired_skills:
        matched_skills = [s for s in desired_skills if any(bs in s or s in bs for bs in b_skills)]
        if matched_skills:
            skill_fraction = min(1.0, len(matched_skills) / len(desired_skills))
            awarded = int(skill_fraction * 20)
            score += awarded
            reasons.append(f"Matched key skills: {', '.join(matched_skills[:3])}")
            if len(matched_skills) < len(desired_skills):
                unmatched = [s for s in desired_skills if s not in matched_skills]
                missing_requirements.append(f"Recommended additional skills: {', '.join(unmatched[:3])}")
        else:
            missing_requirements.append(f"Could benefit from preparatory modules for: {', '.join(desired_skills[:3])}")
    else:
        score += 20
        reasons.append("No specialized prerequisites required; open enrollment profile")

    # 5. Career Goals & Interests Match (15 points)
    desired_interests = [i.lower().strip() for i in requirements.get('desired_interests', [])]
    b_interests = [i.lower().strip() for i in beneficiary_profile.get('interests', [])]
    career_goals = (beneficiary_profile.get('career_goals') or '').lower()

    interest_matches = [i for i in desired_interests if any(bi in i or i in bi for bi in b_interests) or i in career_goals]
    if desired_interests:
        if interest_matches:
            score += 15
            reasons.append(f"Career passion and interests directly aligned with {', '.join(interest_matches[:2])}")
        else:
            score += 5
            reasons.append("General alignment with youth development objectives")
    else:
        score += 15
        reasons.append("Aligned with general empowerment focus")

    final_score = min(100, max(0, score))
    
    return {
        'match_score': final_score,
        'reasons': reasons,
        'missing_requirements': missing_requirements,
        'recommendation': 'STRONGLY_RECOMMENDED' if final_score >= 80 else ('ELIGIBLE' if final_score >= 50 else 'NEEDS_REVIEW')
    }
