import hashlib
from typing import Dict, Any
from enum import Enum


class ExperimentVariant(Enum):
    CONTROL = "control"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"


class ABTestManager:
    def __init__(self):
        self.experiments = {
            "challenge_frequency": {
                "variants": [ExperimentVariant.CONTROL, ExperimentVariant.VARIANT_A],
                "weights": [0.5, 0.5],
                "config": {
                    ExperimentVariant.CONTROL: {"frequency": "daily"},
                    ExperimentVariant.VARIANT_A: {"frequency": "three_times_week"},
                },
            },
            "community_size": {
                "variants": [ExperimentVariant.CONTROL, ExperimentVariant.VARIANT_A],
                "weights": [0.5, 0.5],
                "config": {
                    ExperimentVariant.CONTROL: {"max_members": 12},
                    ExperimentVariant.VARIANT_A: {"max_members": 8},
                },
            },
        }

    def get_variant(self, experiment_name: str, user_id: str) -> ExperimentVariant:
        """Consistent user assignment to experiment variants"""
        if experiment_name not in self.experiments:
            return ExperimentVariant.CONTROL

        # Create consistent hash for user
        hash_input = f"{experiment_name}_{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)

        # Assign based on hash and weights
        experiment = self.experiments[experiment_name]
        threshold = hash_value % 100 / 100.0

        cumulative_weight = 0
        for i, weight in enumerate(experiment["weights"]):
            cumulative_weight += weight
            if threshold < cumulative_weight:
                return experiment["variants"][i]

        return ExperimentVariant.CONTROL

    def get_config(
        self, experiment_name: str, variant: ExperimentVariant
    ) -> Dict[str, Any]:
        """Get configuration for specific experiment variant"""
        return self.experiments[experiment_name]["config"].get(variant, {})


# FastAPI endpoint
@app.get("/api/experiments/{experiment_name}/config")
async def get_experiment_config(
    experiment_name: str,
    user_id: str,
    ab_test_manager: ABTestManager = Depends(get_ab_test_manager),
):
    variant = ab_test_manager.get_variant(experiment_name, user_id)
    config = ab_test_manager.get_config(experiment_name, variant)

    # Log experiment assignment for analysis
    await log_experiment_assignment(user_id, experiment_name, variant.value)

    return {"experiment": experiment_name, "variant": variant.value, "config": config}
