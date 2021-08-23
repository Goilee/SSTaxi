# SSTaxi
## module Moving
### class MoveController  

- `see_red: bool` True if red line before car. **only updates when `get_action() == ACTION_MOVE_TO_CR`**  
**Metods**
- `MoveController(kp=20, kd=25) -> MoveController`  
Constructor.  
*Params:*  
`kp`, `kd` - float koefficient for P- and D- component of PD-regulator
- `get_action() -> action: str`  
Returns current action, must be one of `ACTION_*` constants. Useful after `get_move_values`.
- `new_action(action: str) -> None`  
Sets current action. Must be one of `ACTION_*` constants.
- `get_move_values(env: DuckietownEnv, camera: np.array, dt: float) -> np.array`  
Updates current action and returns nparray with two values: [linear speed, angular speed].  
*Params:*  
`env` - current DuckietownEnv  
`camera` - image from environment  
`dt` - simulation time past from last calling `get_move_values`
### Constants
`ACTION_STOP = 'stop'`  
`ACTION_MOVE_TO_CR = 'crossroad'`  
`ACTION_MOVE_RIGHT = 'right'`  
`ACTION_MOVE_LEFT = 'left'`  
`ACTION_MOVE_TURNOVER = 'turnover'`  