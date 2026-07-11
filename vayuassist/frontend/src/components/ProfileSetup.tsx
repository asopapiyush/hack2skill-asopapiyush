import { useState } from 'react'
import '../styles/ProfileSetup.css'

interface ProfileSetupProps {
  userProfile: any
  token: string
  onProfileUpdate: (profile: any) => void
}

export default function ProfileSetup({
  userProfile,
  token,
  onProfileUpdate
}: ProfileSetupProps) {
  const [familySize, setFamilySize] = useState(userProfile?.family_size || '')
  const [location, setLocation] = useState(userProfile?.location || '')
  const [region, setRegion] = useState(userProfile?.region || 'Maharashtra')
  const [health, setHealth] = useState(userProfile?.health_conditions || '')
  const [loading, setLoading] = useState(false)

  const handleSave = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          family_size: familySize,
          location,
          region,
          health_conditions: health
        })
      })

      if (response.ok) {
        const updated = {
          ...userProfile,
          family_size: familySize,
          location,
          region,
          health_conditions: health
        }
        onProfileUpdate(updated)
      }
    } catch (error) {
      console.error('Profile update error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="profile-setup">
      <div className="setup-content">
        <h3>📋 Complete Your Profile</h3>
        <p>Help us personalize your safety guidance</p>

        <div className="form-group">
          <label>Family Size</label>
          <input
            type="number"
            min="1"
            max="20"
            value={familySize}
            onChange={(e) => setFamilySize(e.target.value)}
            placeholder="Number of people"
          />
        </div>

        <div className="form-group">
          <label>Location Type</label>
          <select value={location} onChange={(e) => setLocation(e.target.value)}>
            <option value="">Select location</option>
            <option value="apartment">Apartment</option>
            <option value="house">House</option>
            <option value="ground_floor">Ground Floor</option>
            <option value="slum">Slum/Temporary Shelter</option>
          </select>
        </div>

        <div className="form-group">
          <label>Region</label>
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="Maharashtra">Maharashtra</option>
            <option value="Gujarat">Gujarat</option>
            <option value="Karnataka">Karnataka</option>
            <option value="Tamil Nadu">Tamil Nadu</option>
            <option value="Telangana">Telangana</option>
          </select>
        </div>

        <div className="form-group">
          <label>Health Conditions (optional)</label>
          <input
            type="text"
            value={health}
            onChange={(e) => setHealth(e.target.value)}
            placeholder="e.g., Diabetes, Asthma"
          />
        </div>

        <button
          onClick={handleSave}
          disabled={loading || !familySize || !location}
          className="save-profile-button"
        >
          {loading ? 'Saving...' : 'Save Profile'}
        </button>
      </div>
    </div>
  )
}
