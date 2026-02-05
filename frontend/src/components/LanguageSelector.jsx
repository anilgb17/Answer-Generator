import React, { useState, useEffect } from 'react'
import { Listbox } from '@headlessui/react'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/24/outline'

const LanguageSelector = ({ onLanguageSelect, disabled = false }) => {
  const [languages, setLanguages] = useState([])
  const [selectedLanguage, setSelectedLanguage] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchLanguages()
  }, [])

  const fetchLanguages = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // In production, this would call the actual API
      // For now, using mock data that matches the backend structure
      const mockLanguages = [
        { code: 'en', name: 'English', native_name: 'English' },
        { code: 'es', name: 'Spanish', native_name: 'Español' },
        { code: 'fr', name: 'French', native_name: 'Français' },
        { code: 'de', name: 'German', native_name: 'Deutsch' },
        { code: 'zh', name: 'Chinese', native_name: '中文' },
        { code: 'ja', name: 'Japanese', native_name: '日本語' },
        { code: 'hi', name: 'Hindi', native_name: 'हिन्दी' },
        { code: 'ar', name: 'Arabic', native_name: 'العربية' },
        { code: 'pt', name: 'Portuguese', native_name: 'Português' },
        { code: 'ru', name: 'Russian', native_name: 'Русский' },
      ]
      
      setLanguages(mockLanguages)
      // Default to English
      const defaultLang = mockLanguages.find(lang => lang.code === 'en')
      setSelectedLanguage(defaultLang)
      onLanguageSelect(defaultLang)
    } catch (err) {
      setError('Failed to load languages')
      console.error('Error fetching languages:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLanguageChange = (language) => {
    setSelectedLanguage(language)
    onLanguageSelect(language)
  }

  if (loading) {
    return (
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Language
        </label>
        <div className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50">
          <p className="text-sm text-gray-500">Loading languages...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Language
        </label>
        <div className="w-full p-3 border border-red-300 rounded-lg bg-red-50">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <Listbox value={selectedLanguage} onChange={handleLanguageChange} disabled={disabled}>
        <Listbox.Label className="block text-sm font-medium text-gray-700 mb-2">
          Select Language
        </Listbox.Label>
        <div className="relative">
          <Listbox.Button
            className={`
              relative w-full cursor-default rounded-lg bg-white py-3 pl-3 pr-10 text-left
              border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-gray-400'}
            `}
          >
            <span className="block truncate">
              {selectedLanguage ? (
                <span>
                  <span className="font-medium">{selectedLanguage.native_name}</span>
                  <span className="text-gray-500 ml-2">({selectedLanguage.name})</span>
                </span>
              ) : (
                'Select a language'
              )}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </span>
          </Listbox.Button>

          <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
            {languages.map((language) => (
              <Listbox.Option
                key={language.code}
                value={language}
                className={({ active }) =>
                  `relative cursor-default select-none py-2 pl-10 pr-4 ${
                    active ? 'bg-blue-100 text-blue-900' : 'text-gray-900'
                  }`
                }
              >
                {({ selected }) => (
                  <>
                    <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                      <span className="font-medium">{language.native_name}</span>
                      <span className="text-gray-500 ml-2">({language.name})</span>
                    </span>
                    {selected && (
                      <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600">
                        <CheckIcon className="h-5 w-5" aria-hidden="true" />
                      </span>
                    )}
                  </>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </div>
      </Listbox>
    </div>
  )
}

export default LanguageSelector
