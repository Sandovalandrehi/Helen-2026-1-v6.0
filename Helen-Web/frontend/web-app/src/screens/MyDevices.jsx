import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGestureNavigation } from '../contexts/gestureNavigationHooks';
import { ScreenHeader } from '../components/layout/ScreenHeader';
import { GlassCard } from '../components/glass/GlassCard';
import { DeviceItem } from '../components/devices/DeviceItem';
import { DeviceModal } from '../components/devices/DeviceModal';
import { ROUTES } from '../config/constants';
import { deviceService } from '../services/deviceService';
import { websocketService } from '../services/websocketService';
import './MyDevices.css';

const MAX_DEVICES = 10;
const WS_BASE = import.meta.env.VITE_WEBSOCKET_URL || 'http://localhost:5001';
const BULB_API_URL = WS_BASE.includes('localhost')
    ? 'http://localhost:5001/tapo/state'
    : WS_BASE + '/tapo-state.php';

/**
 * MyDevices Screen
 * Manage smart home devices with location and type
 * 
 * Features:
 * - Add/Edit/Delete devices
 * - Toggle devices on/off
 * - Edit mode for bulk operations
 * - 10 device limit (full-width cards)
 */
const MyDevices = () => {
    const navigate = useNavigate();
    const { pendingModalGesture, clearPendingModal } = useGestureNavigation();
    
    // State
    const [devices, setDevices] = useState([]);
    const [isEditMode, setIsEditMode] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingDevice, setEditingDevice] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [bulbState, setBulbState] = useState('unknown');   // 'on' | 'off' | 'unknown'
    const [bulbState2, setBulbState2] = useState('unknown'); // 'on' | 'off' | 'unknown'

    // Keep a ref in sync to avoid array deps in callbacks
    const devicesRef = useRef(devices);
    useEffect(() => {
        devicesRef.current = devices;
    }, [devices]);
    
    // Handler functions (declared before useEffect to avoid initialization errors)
    const handleClose = useCallback(() => {
        navigate(ROUTES.HOME);
    }, [navigate]);

    const handleEdit = useCallback(() => {
        setIsEditMode(prev => !prev);
    }, []);

    const handleAdd = useCallback(() => {
        if (devices.length >= MAX_DEVICES) return;
        setEditingDevice(null);
        setIsModalOpen(true);
    }, [devices.length]);
    
    // Handle gesture actions
    useEffect(() => {
        if (pendingModalGesture?.action) {
            if (pendingModalGesture.action === 'add-item') {
                handleAdd();
                clearPendingModal();
            } else if (pendingModalGesture.action === 'edit-item') {
                handleEdit();
                clearPendingModal();
            }
        }
    }, [pendingModalGesture, handleAdd, handleEdit, clearPendingModal]);
    
    // Suscribirse a cambios de estado del foco vía WebSocket + polling cada 5s
    useEffect(() => {
        const fetchState = () => {
            fetch(BULB_API_URL)
                .then(r => r.json())
                .then(data => {
                    setBulbState(data.state ?? 'unknown');
                    setBulbState2(data.state2 ?? 'unknown');
                })
                .catch(() => { setBulbState('unknown'); setBulbState2('unknown'); });
        };

        fetchState(); // fetch inmediato al montar

        const interval = setInterval(fetchState, 5000); // polling cada 5s

        const unsubscribe = websocketService.on('tapo_state', (data) => {
            setBulbState(data.state ?? 'unknown');
            setBulbState2(data.state2 ?? 'unknown');
        });

        return () => {
            clearInterval(interval);
            unsubscribe?.();
        };
    }, []);

    // Fetch devices on mount and subscribe to real-time updates
    useEffect(() => {
        setLoading(true);
        deviceService.getAll()
            .then(data => setDevices(data))
            .catch(() => setError('Error al cargar dispositivos'))
            .finally(() => setLoading(false));

        // Subscribe to device updates via EventEmitter
        const handleDeviceCreated = (device) => {
            setDevices(prev => [...prev, device]);
        };
        
        const handleDeviceUpdated = (device) => {
            setDevices(prev => prev.map(d => d.id === device.id ? device : d));
        };
        
        const handleDeviceDeleted = ({ id }) => {
            setDevices(prev => prev.filter(d => d.id !== id));
        };
        
        const handleDeviceToggled = ({ device }) => {
            setDevices(prev => prev.map(d => d.id === device.id ? device : d));
        };
        
        deviceService.on('device:created', handleDeviceCreated);
        deviceService.on('device:updated', handleDeviceUpdated);
        deviceService.on('device:deleted', handleDeviceDeleted);
        deviceService.on('device:toggled', handleDeviceToggled);
        
        return () => {
            // Cleanup: Remove event listeners
            deviceService.off('device:created', handleDeviceCreated);
            deviceService.off('device:updated', handleDeviceUpdated);
            deviceService.off('device:deleted', handleDeviceDeleted);
            deviceService.off('device:toggled', handleDeviceToggled);
        };
    }, []);

    const handleEditDevice = useCallback((device) => {
        if (isEditMode) {
            setEditingDevice(device);
            setIsModalOpen(true);
        }
    }, [isEditMode]);

    const handleSaveDevice = async (deviceData) => {
        try {
            if (editingDevice) {
                // Update will trigger device:updated event
                await deviceService.update(deviceData.id, deviceData);
            } else {
                setLoading(true);
                // Create will trigger device:created event
                await deviceService.create(deviceData);
            }
        } catch {
            setError('Error al guardar el dispositivo');
        } finally {
            setIsModalOpen(false);
            setEditingDevice(null);
            setLoading(false);
        }
    };

    const handleToggleDevice = useCallback(async (id) => {
        const target = devicesRef.current.find(d => d.id === id);
        try {
            // Toggle will trigger device:toggled event
            await deviceService.toggle(id, !target?.enabled);
        } catch {
            setError('Error al cambiar el estado del dispositivo');
        }
    }, []);

    const handleDeleteDevice = useCallback(async (id) => {
        try {
            // Delete will trigger device:deleted event
            await deviceService.delete(id);
        } catch {
            setError('Error al eliminar el dispositivo');
        }
    }, []);

    const handleEmptyStateClick = () => {
        if (devices.length < MAX_DEVICES) {
            handleAdd();
        }
    };

    const atMaxDevices = devices.length >= MAX_DEVICES;

    return (
        <div className="devices-screen">
            <ScreenHeader 
                title="Mis Dispositivos"
                variant="enhanced"
                onClose={handleClose}
                onEdit={handleEdit}
                onAdd={handleAdd}
                showEditButton={devices.length > 0}
                showAddButton={!atMaxDevices}
                isEditMode={isEditMode}
            />

            {loading && (
                <div className="devices-empty">
                    <GlassCard>
                        <div className="devices-empty__content">
                            <div className="devices-empty__icon">
                                <span className="material-icons-outlined">hourglass_empty</span>
                            </div>
                            <p className="devices-empty__text">Cargando dispositivos...</p>
                        </div>
                    </GlassCard>
                </div>
            )}

            {error && (
                <div className="devices-empty">
                    <GlassCard>
                        <div className="devices-empty__content">
                            <div className="devices-empty__icon">
                                <span className="material-icons-outlined">error</span>
                            </div>
                            <p className="devices-empty__text">{error}</p>
                        </div>
                    </GlassCard>
                </div>
            )}

            {/* Indicadores de Focos RGB — siempre visibles */}
            <div className="bulb-indicator-wrapper">
                <GlassCard className={`bulb-indicator-card bulb-indicator-card--${bulbState}`}>
                    <div className="bulb-indicator__icon">
                        <span className="material-icons-outlined">
                            {bulbState === 'on' ? 'lightbulb' : 'lightbulb_outline'}
                        </span>
                    </div>
                    <div className="bulb-indicator__info">
                        <span className="bulb-indicator__name">Foco RGB 1</span>
                        <span className="bulb-indicator__location">Sala</span>
                    </div>
                    <div className="bulb-indicator__badge">
                        <span className={`bulb-indicator__status bulb-indicator__status--${bulbState}`}>
                            {bulbState === 'on' ? 'Encendido' : bulbState === 'off' ? 'Apagado' : 'Sin conexión'}
                        </span>
                    </div>
                </GlassCard>

                <GlassCard className={`bulb-indicator-card bulb-indicator-card--${bulbState2}`}>
                    <div className="bulb-indicator__icon">
                        <span className="material-icons-outlined">
                            {bulbState2 === 'on' ? 'lightbulb' : 'lightbulb_outline'}
                        </span>
                    </div>
                    <div className="bulb-indicator__info">
                        <span className="bulb-indicator__name">Foco RGB 2</span>
                        <span className="bulb-indicator__location">Sala</span>
                    </div>
                    <div className="bulb-indicator__badge">
                        <span className={`bulb-indicator__status bulb-indicator__status--${bulbState2}`}>
                            {bulbState2 === 'on' ? 'Encendido' : bulbState2 === 'off' ? 'Apagado' : 'Sin conexión'}
                        </span>
                    </div>
                </GlassCard>
            </div>

            {!loading && !error && devices.length === 0 && (
                <div className="devices-empty">
                    <GlassCard 
                        onClick={handleEmptyStateClick}
                        className="devices-empty__card"
                        role="button"
                        tabIndex={0}
                        aria-label="Agregar primer dispositivo"
                    >
                        <div className="devices-empty__content">
                            <div className="devices-empty__icon">
                                <span className="material-icons-outlined">add_home_work</span>
                            </div>
                            <p className="devices-empty__text">Sin Dispositivos</p>
                        </div>
                    </GlassCard>
                </div>
            )}

            {!loading && !error && devices.length > 0 && (
                <div className="devices-list">
                    {devices.map(device => (
                        <DeviceItem
                            key={device.id}
                            device={device}
                            isEditMode={isEditMode}
                            onToggle={handleToggleDevice}
                            onEdit={handleEditDevice}
                            onDelete={handleDeleteDevice}
                        />
                    ))}

                    {devices.length >= MAX_DEVICES && (
                        <div className="devices-max-message">
                            <GlassCard>
                                <p className="devices-max-message__text">
                                    <span className="material-icons-outlined">info</span>
                                    Máximo de 10 dispositivos alcanzados
                                </p>
                            </GlassCard>
                        </div>
                    )}
                </div>
            )}

            <DeviceModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setEditingDevice(null);
                }}
                onSave={handleSaveDevice}
                device={editingDevice}
            />
        </div>
    );
};

export default MyDevices;