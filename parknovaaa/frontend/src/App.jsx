import { useState, useEffect } from 'react';
import { 
  LayerGroup, 
  MapContainer, 
  TileLayer, 
  CircleMarker, 
  Popup, 
  useMap 
} from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import { 
  LayoutDashboard, 
  Car, 
  Calendar, 
  User, 
  Settings, 
  LogOut, 
  MapPin, 
  Clock, 
  TrendingUp,
  Search,
  Bell,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  QrCode,
  IndianRupee
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8080/api';

// Helper to center map
function ChangeView({ center, zoom }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

function App() {
  const [slots, setSlots] = useState([]);
  const [stats, setStats] = useState({ total: 0, available: 0, occupied: 0 });
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [activeBooking, setActiveBooking] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [view, setView] = useState('dashboard'); // dashboard, payment, receipt
  const [transactionId, setTransactionId] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const fetchData = async () => {
    try {
      const [slotsRes, statsRes, activeRes] = await Promise.all([
        axios.get(`${API_BASE}/slots`),
        axios.get(`${API_BASE}/stats`),
        axios.get(`${API_BASE}/active-booking`).catch(() => ({ data: null }))
      ]);
      setSlots(slotsRes.data);
      setStats(statsRes.data);
      if (activeRes.data) {
        setActiveBooking(activeRes.data);
        if (activeRes.data.paymentStatus === 'PENDING') {
          setView('payment');
        }
      }
      setLoading(false);
    } catch (err) {
      console.error("Error fetching data:", err);
      setLoading(false);
    }
  };

  const handleBook = async () => {
    if (!selectedSlot) return;
    try {
      const res = await axios.post(`${API_BASE}/book/${selectedSlot.id}`);
      setActiveBooking(res.data);
      setView('payment');
    } catch (err) {
      alert(err.response?.data || "Booking failed");
    }
  };

  const handleConfirmPayment = async () => {
    if (!transactionId) return;
    try {
      const res = await axios.post(`${API_BASE}/payment/confirm`, {
        bookingId: activeBooking.id,
        transactionId: transactionId
      });
      setActiveBooking(res.data);
      setView('receipt');
    } catch (err) {
      alert(err.response?.data || "Payment confirmation failed");
    }
  };

  if (loading) return <div className="loading-screen">Initializing Systems...</div>;

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar glass-effect">
        <div className="brand">
          <div className="logo-icon">PN</div>
          <h2>ParkNova</h2>
        </div>
        <nav>
          <a href="#" onClick={() => setView('dashboard')} className={`nav-link ${view === 'dashboard' ? 'active' : ''}`}><LayoutDashboard size={20} /> Dashboard</a>
          <a href="#" className="nav-link"><Car size={20} /> My Bookings</a>
          <a href="#" className="nav-link"><Calendar size={20} /> Schedule</a>
          <a href="#" className="nav-link"><User size={20} /> Profile</a>
          <div className="nav-divider"></div>
          <a href="#" className="nav-link"><Settings size={20} /> Settings</a>
          <a href="#" className="nav-link logout"><LogOut size={20} /> Logout</a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="main-header glass-effect">
          <div className="header-search">
            <Search size={18} className="search-icon" />
            <input type="text" placeholder="Search for slots, locations..." />
          </div>
          <div className="header-actions">
            <div className="time-display glass-effect">
              {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
            <button className="icon-btn glass-effect"><Bell size={20} /></button>
            <div className="user-profile">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Pavan" alt="User" />
              <span>Pavan Kalyan</span>
            </div>
          </div>
        </header>

        <div className="content-inner animate-fade-in">
          {view === 'dashboard' && (
            <>
              <section className="stats-grid">
                <StatCard label="Total Capacity" value={stats.total} icon={Car} color="#00e5ff" />
                <StatCard label="Available" value={stats.available} icon={MapPin} color="#00ff88" />
                <StatCard label="Occupied" value={stats.occupied} icon={Clock} color="#ff4444" />
                <StatCard label="Active Status" value={activeBooking ? 'User In' : 'Ready'} icon={TrendingUp} color="#ffcc00" />
              </section>

              <section className="dashboard-main">
                <div className="parking-layout glass-card">
                  <div className="section-header">
                    <h3>Interactive Map Explorer</h3>
                    <div className="map-legend">
                      <span className="legend-item"><span className="dot available"></span> Available</span>
                      <span className="legend-item"><span className="dot occupied"></span> Occupied</span>
                    </div>
                  </div>
                  
                  <div className="map-wrapper" style={{ height: '400px', borderRadius: '20px', overflow: 'hidden', marginBottom: '1.5rem' }}>
                    <MapContainer center={[17.4504, 78.3811]} zoom={15} style={{ height: '100%', width: '100%' }}>
                      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                      {slots.map(slot => (
                        slot.latitude && (
                          <CircleMarker 
                            key={slot.id}
                            center={[slot.latitude, slot.longitude]}
                            radius={10}
                            pathOptions={{ 
                              fillColor: slot.status === 'AVAILABLE' ? '#00ff88' : '#ff4444',
                              color: 'white',
                              weight: 2,
                              fillOpacity: 0.8
                            }}
                            eventHandlers={{
                              click: () => setSelectedSlot(slot)
                            }}
                          >
                            <Popup>
                              <div className="map-popup">
                                <strong>Slot {slot.slotNumber}</strong><br/>
                                {slot.location} • ₹{slot.hourlyRate}/hr
                              </div>
                            </Popup>
                          </CircleMarker>
                        )
                      ))}
                    </MapContainer>
                  </div>

                  <div className="slots-grid">
                    {slots.map(slot => (
                      <div 
                        key={slot.id} 
                        className={`slot-item ${slot.status === 'AVAILABLE' ? 'available' : 'occupied'} ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
                        onClick={() => slot.status === 'AVAILABLE' && setSelectedSlot(slot)}
                      >
                        <span className="slot-id">{slot.slotNumber}</span>
                        <span className="slot-type">{slot.location}</span>
                        {slot.status !== 'AVAILABLE' && <Car size={16} className="car-icon" />}
                      </div>
                    ))}
                  </div>
                </div>

                <aside className="booking-summary glass-card">
                  <h3>Quick Booking</h3>
                  {selectedSlot ? (
                    <div className="booking-details animate-fade-in">
                      <div className="detail-row">
                        <span>Selected Slot:</span>
                        <strong>{selectedSlot.slotNumber}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Hourly Rate:</span>
                        <strong>₹{selectedSlot.hourlyRate}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Location:</span>
                        <strong>{selectedSlot.location}</strong>
                      </div>
                      <button onClick={handleBook} className="btn-primary w-full mt-8">Confirm Booking</button>
                    </div>
                  ) : activeBooking ? (
                    <div className="active-booking-info">
                       <CheckCircle2 color="#00ff88" size={48} className="mt-4 mb-4" />
                       <p>You have an active booking: <strong>{activeBooking.slot.slotNumber}</strong></p>
                       <button onClick={() => setView('receipt')} className="btn-secondary w-full mt-4">View Receipt</button>
                    </div>
                  ) : (
                    <div className="no-selection">
                      <Car size={48} className="fade-icon" />
                      <p>Select a slot from the map or grid to proceed</p>
                    </div>
                  )}
                </aside>
              </section>
            </>
          )}

          {view === 'payment' && activeBooking && (
            <div className="payment-view glass-card animate-fade-in max-w-2xl mx-auto text-center">
              <QrCode size={48} className="mx-auto mb-4 text-accent-primary" />
              <h2 className="text-2xl font-bold mb-2">Secure Payment</h2>
              <p className="text-secondary mb-8">Scan to pay ₹{activeBooking.slot.hourlyRate} and secure your spot.</p>
              
              <div className="payment-qr-wrapper mb-8">
                <img src="http://localhost:8080/images/payment_qr.png" alt="QR" style={{ width: '200px', borderRadius: '15px', border: '5px solid white' }} />
              </div>

              <div className="payment-form text-left">
                <label className="stat-label">Transaction Reference ID</label>
                <input 
                  type="text" 
                  value={transactionId}
                  onChange={(e) => setTransactionId(e.target.value)}
                  placeholder="Enter 12-digit Ref No."
                  className="w-full bg-tertiary border p-3 rounded-xl mb-4"
                />
                <button onClick={handleConfirmPayment} className="btn-primary w-full py-4 text-lg">Confirm & Generate Receipt</button>
                <a href={`upi://pay?pa=7382025805@ybl&pn=Pavan&am=${activeBooking.slot.hourlyRate}`} className="btn-secondary w-full mt-4 block text-center">Open Payment App</a>
              </div>
            </div>
          )}

          {view === 'receipt' && activeBooking && (
            <div className="receipt-view glass-card animate-fade-in max-w-lg mx-auto">
              <div className="receipt-header text-center border-b pb-6 mb-6">
                <CheckCircle2 color="#00ff88" size={64} className="mx-auto mb-4" />
                <h2 className="text-2xl font-bold">Booking Confirmed</h2>
                <span className="text-secondary">Ref: {activeBooking.transactionReference}</span>
              </div>
              <div className="receipt-body space-y-4">
                <ReceiptRow label="Slot ID" value={activeBooking.slot.slotNumber} />
                <ReceiptRow label="Entry Token" value={activeBooking.qrCode} highlight />
                <ReceiptRow label="Location" value={activeBooking.slot.location} />
                <ReceiptRow label="Start Time" value={new Date(activeBooking.startTime).toLocaleTimeString()} />
              </div>
              <button onClick={() => setView('dashboard')} className="btn-primary w-full mt-10">Back to Dashboard</button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="glass-card stat-card">
      <div className="stat-info">
        <span className="stat-label">{label}</span>
        <h3 className="stat-value">{value}</h3>
      </div>
      <div className="stat-icon-wrapper" style={{ backgroundColor: `${color}15`, color: color }}>
        <Icon size={24} />
      </div>
    </div>
  );
}

function ReceiptRow({ label, value, highlight }) {
  return (
    <div className="detail-row">
      <span className="text-secondary">{label}</span>
      <strong className={highlight ? 'text-accent-primary text-xl' : ''}>{value}</strong>
    </div>
  );
}

export default App;
