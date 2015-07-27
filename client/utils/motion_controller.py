from collections import deque
from shared.constants.movement import MOVEMENT_VALUES

import sfml as sf
import time

class PredictionState:

    def __init__(self, id, delta):
        self.id = id
        self.delta = delta
        self.applied = False
        self.fixed = False

        self.predictedPosition = None

    @property
    def position(self):
        return self.predictedPosition

    def simulate(self, position, velocity):
        if self.predictedPosition is None:
            dx, dy = self.delta
            self.predictedPosition = sf.Vector2(position.x + (dx * velocity.x),
                position.y + (dy * velocity.y))

        return self.predictedPosition

    def __str__(self):
        state = '<Prediction: '
        if self.applied:
            state += 'applied '
        if self.fixed:
            state += 'fixed '
        state += '({delta[0]}, {delta[1]}) - id: {id}'
        if self.predictedPosition is not None:
            state += ' - predicted position: ({position.x}, {position.y})'
        state += '>'
        return state.format(id=self.id, delta=self.delta, position=self.predictedPosition)

class PositionState:

    def __init__(self, position):
        self.predictedPosition = position

    def simulate(self, position, velocity):
        return self.predictedPosition

    @property
    def position(self):
        return self.predictedPosition

    def __str__(self):
        return '<Server position: ({pos.x}, {pos.y})>'.format(pos=self.position)

class RemoteController:

    def __init__(self, controlledObject):
        self.object = controlledObject
        self.positionsToApply = deque()

    def enqueuePosition(self, position):
        if not isinstance(position, PositionState):
            position = PositionState(position)

        self.positionsToApply.append(position)

    def validate(self, packet):
        x, y, vx, vy = packet.read('!iiii')

        self.object.velocity = sf.Vector2(vx, vy)
        self.object.enqueuePositionUpdate(sf.Vector2(x, y))

    def apply(self):
        if self.positionsToApply:
            return self.positionsToApply.popleft()
        else:
            return None

class LocalController:

    def __init__(self, controlledObject):
        self.object = controlledObject
        self.predictionsTable = {}
        self.predictionsToApply = deque()

        self.lastPredictionTime = 0
        self.lastPacketTime = 0
        self.lastTick = 0

        self.tickTime = 10

    def createPrediction(self, pId, delta):
        self.predictionsTable[pId] = PredictionState(pId, delta)

    def enqueuePrediction(self, prediction):
        self.predictionsToApply.append(prediction)

    def predict(self, predictionId, direction):
        """
        Enqueue a prediction for the direction.
        """
        self.createPrediction(predictionId, MOVEMENT_VALUES[direction])
        self.enqueuePrediction(self.predictionsTable[predictionId])

    def validate(self, packet):
        """
        Check if a prediction is good.
        If not, the controller *fix* it.
        """
        self.lastPacketTime = time.time()
        x, y, vx, vy = packet.read('!iiii')

        position = sf.Vector2(x, y)
        velocity = sf.Vector2(vx, vy)

        predictionId = None
        if packet.canReadUint64():
            predictionId = packet.readUint64()

        self.object.velocity = velocity

        # It's a regular update, let's be sure that we won't trouble our prediction state.
        if predictionId is None:
            # If we don't have any predictions, go ahead and refresh our position.
            if len(self.predictionsToApply) == 0 or self.lastPredictionTime > packet.time:
                self.predictionsToApply.append(PositionState(position))
        # This is a prediction confirmation, let's compare between our prediction and the reality.
        else:
            preState = self.predictionsTable[predictionId]
            if preState.position != position:
                # Our prediction was false, fix it.
                self.fix(preState, position)

    def fix(self, predictionState, serverPosition):
        """
        Fix a prediction and replay it if the state has been already applied.
        """
        predictionState.predictedPosition = serverPosition
        predictionState.fixed = True

        if predictionState.applied:
            predictionState.applied = False
            self.enqueuePrediction(predictionState)

    def apply(self):
        """
        Try to return the next prediction from the current state.
        """
        while (100 * (time.time() - self.lastTick)) < self.tickTime:
            pass

        self.lastTick = time.time()

        if self.predictionsToApply:
            state = self.predictionsToApply.popleft()
            return state
        else:
            return None

    def applied(self, predictedState):
        """
        Reload the predicted state inside the controller.
        """
        if isinstance(predictedState, PredictionState):
            predictedState.applied = True
            self.lastPredictionTime = time.time()
            self.predictionsTable[predictedState.id] = predictedState
