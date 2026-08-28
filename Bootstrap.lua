local addonName = ...

local function registerDictionary()
  local addon = WordHunterWoW_Addon
  if not addon or not addon.RegisterDictionaryProvider or type(WordHunterWoW_Dictionary_PTBR) ~= "table" then return end
  addon.RegisterDictionaryProvider("ptBR", addonName, WordHunterWoW_Dictionary_PTBR)
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:SetScript("OnEvent", function(_, _, loaded)
  if loaded == addonName then registerDictionary() end
end)

-- WordHunterWoW is a required dependency, so its provider API is already available.
-- Register immediately as well as on ADDON_LOADED to avoid load-order edge cases.
registerDictionary()
