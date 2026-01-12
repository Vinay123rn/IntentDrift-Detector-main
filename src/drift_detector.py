import numpy as np
from sentence_transformers import SentenceTransformer, util


class IntentDriftDetector:
    """
    Detects INTENT drift (not topic drift) by tracking functional intent states
    over a sequence of user utterances.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        drift_persistence: int = 1,
        confidence_threshold: float = 0.30,
    ):
        """
        drift_persistence:
            Number of consecutive turns a new intent must appear
            before confirming drift (prevents noise).

        confidence_threshold:
            Minimum similarity required to assign an intent.
        """

        self.model = SentenceTransformer(model_name)
        self.drift_persistence = drift_persistence
        self.confidence_threshold = confidence_threshold

        self.intent_anchors = {

    # ============================================================
    # INTEREST → Motivation, optimism, aspiration (NO evaluation)
    # ============================================================
    "interest": [
        # Excitement & ambition
        "I am excited for the placement season",
        "I really want to get placed this year",
        "I am motivated for placements",
        "I am looking forward to company visits",
        "I want to crack a dream company",
        "I am enthusiastic about the opportunities",
        "I hope to get a good offer",
        "I am confident about my preparation",
        "I am ready for the challenge",
        "this placement season looks promising",

        # Career goals
        "getting a job is my top priority",
        "I want to secure my future",
        "I want to start my career properly",
        "I want a stable job after college",
        "I want industry exposure",
        "I want to gain real world experience",
        "I want to prove myself in interviews",

        # Role / company interest
        "I am interested in software roles",
        "I want a software developer role",
        "I am interested in analyst profiles",
        "I want to join a reputed company",
        "I am keen on joining an MNC",
        "startups really interest me",
        "I am open to good opportunities",

        # Preparation mindset
        "I am preparing hard for interviews",
        "I am practicing coding daily",
        "I am focused on placement preparation",
        "I am working on my skills",
        "I am taking placements seriously",

        # Positive emotions / outlook
        "I feel hopeful",
        "I feel positive about my chances",
        "I believe things will work out",
        "I trust my preparation",

        # Future-oriented optimism (NOT decisions)
        "I am excited for future placements",
        "I am planning for next year",
        "I am looking forward to next season",
        "I am ready for the next challenge",
    ],

    # ============================================================
    # INFORMATION → Facts, rules, process, clarification
    # ============================================================
    "information": [
        # Placement process
        "how does the placement process work",
        "what is the placement procedure",
        "what are the selection rounds",
        "how many interview rounds are there",
        "what happens after registration",

        # Eligibility & rules
        "what is the eligibility criteria",
        "does cgpa matter",
        "are backlogs allowed",
        "is branch eligibility strict",
        "is there any bond period",
        "can I sit for multiple companies",

        # Salary & role details
        "what is the ctc offered",
        "what is the in hand salary",
        "what is the average package",
        "what is the job role",
        "what responsibilities will I have",

        # Company & logistics
        "which companies are visiting",
        "when is the interview",
        "where is the job location",
        "is it onsite or remote",
        "what is the joining date",

        # Preparation queries
        "how should I prepare for placements",
        "what topics should I focus on",
        "what kind of questions are asked",
        "how difficult are the interviews",
        "what skills are required",
    ],

    # ============================================================
    # COMPARISON → Trade-offs, evaluation between options
    # ============================================================
    "comparison": [
        # Role comparisons
        "product role or service role",
        "developer or analyst role",
        "technical role vs non technical role",
        "core job vs IT job",

        # Company type comparison
        "startup or mnc",
        "big company or small company",
        "product company vs service company",
        "mass recruiter vs niche company",

        # Salary vs growth
        "ctc or learning which is better",
        "salary vs work life balance",
        "money or career growth",
        "brand name or role quality",

        # Offer decisions (comparison, NOT action)
        "should I take this offer or wait",
        "is it better to wait for a dream company",
        "should I accept this job",
        "should I look for off campus options",

        # Alternatives
        "job or higher studies",
        "placements or masters",
        "on campus or off campus",
        "job or entrepreneurship",

        # Self evaluation
        "am I expecting too much",
        "am I lagging behind others",
        "is my situation worse than average",
        "are others also struggling like me",
    ],

    # ============================================================
    # COMPLAINT → Anxiety, dissatisfaction, negative evaluation
    # ============================================================
    "complaint": [
        # Anxiety & fear
        "I am stressed about placements",
        "I feel anxious about my future",
        "I am worried I will not get placed",
        "I feel insecure about my career",
        "I am scared about what will happen",

        # Emotional exhaustion
        "this process is exhausting",
        "I feel mentally drained",
        "I am burned out",
        "this pressure is too much",
        "I am tired of preparing",

        # Dissatisfaction with outcomes
        "placements are not going well",
        "companies coming are not good",
        "packages are very low",
        "placement cell is not helping",
        "opportunities are limited",

        # Rejections & self doubt
        "I am tired of getting rejected",
        "I failed multiple interviews",
        "I feel underprepared",
        "I doubt my abilities",
        "others are getting placed not me",

        # Comparative dissatisfaction / decline
        "packages are lower than expected",
        "this year packages are lower",
        "offers are worse compared to last year",
        "placements have gone down this year",
        "the quality of offers has decreased",
        "salary trends look bad this year",
        "packages are not improving",
        "the pay offered is disappointing",
        "compensation seems poor this time",
        "placements are weaker than before",

        # Subtle negative evaluation
        "this does not look encouraging",
        "things do not look good this year",
        "the situation seems worse now",
        "this feels like a downgrade",
        "overall outcome looks disappointing",

        # Negative outlook
        "this season feels bad",
        "everything feels uncertain",
        "I regret my decisions",
        "I feel helpless",
        "I feel lost about what to do",
    ],

    # ============================================================
    # DECISION → Clear action, commitment, exit or acceptance
    # ============================================================
    "decision": [
        # Acceptance
        "I accepted the offer",
        "I have decided to join this company",
        "I am finalizing this job",
        "I will sign the offer letter",
        "I am joining this role",

        # Rejection / exit
        "I will reject this offer",
        "I am quitting the placement process",
        "I will stop attending interviews",
        "I am opting out of placements",
        "I am done with this process",

        # Alternative paths (ACTIONABLE)
        "I will try off campus",
        "I will go for higher studies",
        "I will prepare for competitive exams",
        "I will pursue a masters degree",
        "I will choose another career path",

        # Soft but decisive
        "I am leaning towards another option",
        "I have decided to change my plan",
        "I will not continue with this approach",
        "I am committing to this choice",
        "this is my final decision",

        # Closure
        "this is my final choice",
        "I am clear about my next step",
        "I am moving forward with this plan",
        "I am closing this chapter",
        "I am done with placements",
    ],
}



        # Precompute anchor embeddings
        self.intent_embeddings = self._embed_intent_anchors()

        # Conversation state
        self.intent_history = []
        self.candidate_intent = None
        self.candidate_count = 0

    # ------------------------------------------------------------------

    def _embed_intent_anchors(self):
        """
        Compute a single embedding per intent
        by averaging its anchor sentence embeddings.
        """
        intent_embeddings = {}

        for intent, anchors in self.intent_anchors.items():
            emb = self.model.encode(anchors, convert_to_tensor=True)
            intent_embeddings[intent] = emb.mean(dim=0)

        return intent_embeddings

    # ------------------------------------------------------------------

    def _detect_intent(self, utterance: str):
        """
        Assigns an intent label to a single utterance
        based on similarity to intent anchors.
        """
        utter_emb = self.model.encode(utterance, convert_to_tensor=True)

        best_intent = None
        best_score = -1.0

        for intent, anchor_emb in self.intent_embeddings.items():
            score = util.cos_sim(utter_emb, anchor_emb).item()
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_score < self.confidence_threshold:
            return "unknown", best_score

        return best_intent, best_score

    # ------------------------------------------------------------------

    def update(self, utterance: str):
        """
        Process a new utterance and detect intent drift if it occurs.
        Returns a structured result.
        """

        detected_intent, confidence = self._detect_intent(utterance)

        result = {
            "utterance": utterance,
            "detected_intent": detected_intent,
            "confidence": round(confidence, 3),
            "intent_drift": False,
            "previous_intent": None,
            "current_intent": None,
            "explanation": None,
        }

        # First turn
        if not self.intent_history:
            # If start is unknown, we just record it but it's not a "state" we drift FROM later
            # However, simpler to just start history.
            # But requirement says "UNKNOWN is NOT an intent state".
            # If first msg is unknown, let's say current is unknown.
            if detected_intent == "unknown":
                result["current_intent"] = "unknown"
                result["explanation"] = "Intent unknown."
                return result
            
            self.intent_history.append(detected_intent)
            result["current_intent"] = detected_intent
            result["explanation"] = "Initial intent established."
            return result

        last_intent = self.intent_history[-1]
        result["previous_intent"] = last_intent

        # GUARD: If detected intent is UNKNOWN, do nothing.
        # "UNKNOWN must NEVER participate in drift transitions"
        if detected_intent == "unknown":
            result["current_intent"] = last_intent
            result["explanation"] = "Input out of scope or unclear. Intent state maintained."
            return result
        
        # If we reach here, detected_intent is VALID (not unknown).

        # Special Case: If previous was unknown (e.g. from start), initialize state
        if last_intent == "unknown":
            self.intent_history.append(detected_intent)
            result["current_intent"] = detected_intent
            result["explanation"] = f"Intent identified: '{detected_intent}'."
            return result

        # Normal Drift Logic
        
        # Same intent → reset candidate drift
        if detected_intent == last_intent:
            self.candidate_intent = None
            self.candidate_count = 0
            # We don't necessarily need to append to history if it's the same, 
            # but existing logic did. Let's keep it simple or just not append?
            # Existing logic appended. Let's append to keep history trace if needed,
            # or just leave it. The prompt says "DO NOT update internal intent state" for UNKNOWN.
            # For same intent, state is same.
            result["current_intent"] = detected_intent
            result["explanation"] = "Intent remains stable."
            return result

        # Potential new intent → persistence check
        if detected_intent == self.candidate_intent:
            self.candidate_count += 1
        else:
            self.candidate_intent = detected_intent
            self.candidate_count = 1

        # Confirm drift only if persistent
        if self.candidate_count >= self.drift_persistence:
            self.intent_history.append(detected_intent)
            self.candidate_intent = None
            self.candidate_count = 0

            result["intent_drift"] = True
            result["current_intent"] = detected_intent
            result["explanation"] = (
                f"Intent drift detected: conversation shifted from "
                f"'{last_intent}' to '{detected_intent}'."
            )
            return result

        # Drift not yet confirmed
        result["current_intent"] = last_intent
        result["explanation"] = (
            "Possible intent change detected but not yet stable."
        )
        return result

    # ------------------------------------------------------------------

    def reset(self):
        """Reset conversation state."""
        self.intent_history = []
        self.candidate_intent = None
        self.candidate_count = 0
