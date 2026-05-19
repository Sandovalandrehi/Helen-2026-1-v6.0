import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { GESTURE_ACTIONS, HOME_ACTION_TYPES, ROUTES } from '../config/constants';
import { GestureNavigationStateContext, GestureNavigationActionsContext } from './gestureNavigationContexts';
import { predictionService } from '../services/predictionService';
import { useCameraActions } from './cameraHooks';

/**
 * GestureNavigationProvider
 *
 * Listens to prediction:result IPC events from the Main Process and executes the appropriate UI action (navigation, modal, or context-dependent action) based on the detected gesture.
 * Follows the same architectural pattern as CameraContext for consistency.
 *
 * Architecture:
 * - Main Process (predictionService) sends IPC events with gesture data.
 * - This context listens and dispatches the appropriate UI action.
 * - Navigation: Direct route change via React Router.
 * - Modals: Sets pending state, consumed by HomeScreen.
 * - Actions: Context-dependent, consumed by individual screens.
 */
export const GestureNavigationProvider = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { handleSignDetection } = useCameraActions();

  const [lastGesture, setLastGesture] = useState(null);
  const [pendingModalGesture, setPendingModalGesture] = useState(null);

  /**
   * Execute the appropriate action based on the gesture type.
   */
  const executeGestureAction = useCallback((gesture, confidence) => {
    // Log execution of gesture action
    console.log(`Executing gesture: ${gesture} (confidence: ${confidence})`);
    
    const action = GESTURE_ACTIONS[gesture];
    
    if (!action) {
      // Warn if gesture is not recognized
      console.warn(`Unknown gesture: ${gesture}`);
      return;
    }

    setLastGesture({ gesture, confidence, timestamp: Date.now() });

    // Execute based on action type
    switch (action.type) {
      case HOME_ACTION_TYPES.NAVIGATE:
        // Log navigation action
        console.log(`Navigating to: ${action.route}`);
        navigate(action.route);
        break;

      case HOME_ACTION_TYPES.MODAL:
        // Log modal opening action
        console.log(`Opening modal: ${action.modal}`);
        // Store modal request - will be picked up by HomeScreen component
        setPendingModalGesture({ modal: action.modal, timestamp: Date.now() });
        // Navigate to HOME if not already there (modals only work on HomeScreen)
        if (location.pathname !== ROUTES.HOME) {
          navigate(ROUTES.HOME);
        }
        break;

      case 'action':
        // Log context-dependent action execution
        console.log(`Executing action: ${action.action}`);
        
        // Validate context for agregar/editar actions
        if (action.action === 'add-item' || action.action === 'edit-item') {
          // Only allow on Alarms and Devices screens
          const validRoutes = [ROUTES.ALARMS, ROUTES.DEVICES];
          
          if (!validRoutes.includes(location.pathname)) {
            // Warn if action is not valid on the current route
            console.warn(`Action ${action.action} not valid on route: ${location.pathname}`);
            console.log(`Navigate to Alarms or Devices first to use this gesture`);
            return; // Don't set pendingModalGesture
          }
          
          // Log valid action on current route
          console.log(`Action ${action.action} valid on route: ${location.pathname}`);
        }
        
        // Context-dependent actions handled by screen components
        setPendingModalGesture({ action: action.action, timestamp: Date.now() });
        break;

      default:
        // Warn if action type is unknown
        console.warn(`Unknown action type: ${action.type}`);
    }
  }, [navigate, location]);

  /**
   * Clear the pending modal gesture (called by screens after consuming).
   */
  const clearPendingModal = useCallback(() => {
    setPendingModalGesture(null);
  }, []);

  /**
   * Listen to IPC prediction:result events from the Main Process.
   */
  useEffect(() => {
    if (!window.electronBackend) {
      // Web mode: use WebSocket predictionService
      console.log('Web mode - connecting gesture navigation via WebSocket');
      predictionService.initialize();

      const unsubscribe = predictionService.subscribe((prediction) => {
        const { gesture, confidence } = prediction;
        console.log(`Received prediction via WebSocket: ${gesture} (${confidence})`);
        if (confidence >= 0.7) {
          handleSignDetection(gesture);
          executeGestureAction(gesture, confidence);
        }
      });

      return unsubscribe;
    }

    // Electron IPC mode
    const handlePredictionResult = (event) => {
      const { gesture, confidence } = event;
      console.log(`Received prediction from Main Process: ${gesture} (${confidence})`);
      if (confidence >= 0.7) {
        executeGestureAction(gesture, confidence);
      }
    };

    window.electronBackend.on('prediction:result', handlePredictionResult);
    console.log('Subscribed to prediction:result events');

    return () => {
      console.log('Unsubscribing from prediction:result events');
    };
  }, [executeGestureAction]);

  // Memoize context values to prevent unnecessary re-renders
  const state = useMemo(() => ({
    lastGesture,
    pendingModalGesture,
  }), [lastGesture, pendingModalGesture]);

  const actions = useMemo(() => ({
    executeGestureAction,
    clearPendingModal,
  }), [executeGestureAction, clearPendingModal]);

  return (
    <GestureNavigationActionsContext.Provider value={actions}>
      <GestureNavigationStateContext.Provider value={state}>
        {children}
      </GestureNavigationStateContext.Provider>
    </GestureNavigationActionsContext.Provider>
  );
};
