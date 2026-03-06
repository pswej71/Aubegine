def select_model_mode(has_external_data: bool, manual_mode: str = 'auto'):
    """
    Model Switching Logic (Layer 9).
    Manual override vs Auto intelligence.
    """
    if manual_mode != 'auto':
        return manual_mode
    
    # Auto logic: IF environmental data exists THEN combined ELSE internal
    if has_external_data:
        return 'combined'
    else:
        return 'internal'
