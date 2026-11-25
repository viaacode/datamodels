# Migration legacy ontologies to the new hetarchief model

Prepared from the workspace sources on 24 November 2026 and revised against the current RDFS model on 25 November 2026.

Most used terms have a clear destination in the consolidated `ha:` namespace, while PREMIS, PROV and ODRL terms largely retain their external IRIs. A complete migration cannot be implemented as a namespace replacement: several properties change their value structure or meaning, and some target declarations conflict with the source shapes. The tables below distinguish direct mappings, required transformations and unresolved decisions.

## Scope and evidence

The inventory starts with active `sh:targetClass`, `sh:class` and `sh:path` statements in the source shapes, including nested `sh:or` alternatives and reusable property shapes. It also includes the resource IRIs in `sh:in` lists, because those values must migrate with their properties. Comments, unused prefix declarations, SHACL machinery and ontology-document metadata are excluded. A term occurring in several files has one crosswalk entry. Datatypes retain their IRIs unless a specific conversion is identified below.

| Code | Source shape file | Distinct classes used | Distinct properties used |
| --- | --- | ---: | ---: |
| D | `description/description.shacl.ttl` | 49 | 105 |
| E | `events/events.shacl.ttl` | 9 | 18 |
| O | `objects/objects.shacl.ttl` | 16 | 50 |
| G | `organizations/organizations.shacl.ttl` | 18 | 42 |
| R | `rights/rights.shacl.ttl` | 16 | 17 |

The five source files contain **90 distinct classes and 211 distinct properties**. Counts overlap between source files and must not be summed.

Destinations were checked against `hetarchief/model.rdfs.ttl` and its three imported extracts: `hetarchief/external/premis.rdfs.ttl`, `hetarchief/external/prov.rdfs.ttl` and `hetarchief/external/odrl.rdfs.ttl`. Legacy RDFS definitions in the five source directories and `ontologies/` clarify meaning where necessary; selected local SKOS files clarify enumerated values. Terms defined only in legacy RDFS, but never used by the source shapes, are outside this crosswalk. In particular, no `haEvt:` classes or properties occur in the event shapes.

The crosswalk uses the RDFS model to determine target mappings. The draft `hetarchief/model.shacl.ttl` needs alignment before migration acceptance. Production data profiling is part of the execution plan.

An explicit `owl:equivalentClass` or `owl:equivalentProperty` is stronger evidence than `rdfs:seeAlso`. The latter helps identify a candidate but does not assert equivalence. Local renames were checked against definitions and comments. RDFS domain/range statements imply types; they are not validation constraints. Conflicting declarations below therefore identify both semantic risks and decisions needed before a migration validation profile can be written.

## Rules for Naming and labels

| Source construct | Target convention | Example |
| --- | --- | --- |
| Class | Singular `PascalCase` | `ha:DigitalRepresentation` |
| Direct property | Active third-person `lowerCamelCase` | `ha:creates` |
| Existing reverse property | Configured reverse name in `lowerCamelCase` | `ha:isCreatedBy` |
| Possession or part relation | Use `has…` or the configured reverse expression | `ha:hasName`, `ha:hasPart`, `ha:isPartOf` |
| Named shape | `PascalCase` | `ha:PersonShape`, `ha:PersonHasNameShape` |
| Scheme, or ontology | `lowerCamelCase` | `ha:contentRange`, `ha:descriptionModel` |
| Concept | `kebab-case` | `ha:available-for-consultation` |
| Boolean property | Express what `true` affirms. Use `is…` for a state, `has…` for presence, or `can…` for a capability. | `ha:isPublic`, `ha:hasMissingAudioReels`, `ha:canBeReused` |

- Apply configured acronyms, irregular verbs, per-URI overrides, and names for existing inverse pairs. 
- Keep the source inverse axioms and create no new inverse properties. 
- Align English `rdfs:label` and `sh:name` with the configured label for remapped terms. 
- Preserve Dutch and French text, contextual names and constraints on anonymous shapes, literal lexical forms, and list order. 
- Resolve relative IRIs against the source base and keep blank-node identities scoped to each source file.
- Identify Boolean properties from `rdfs:range xsd:boolean` or `sh:datatype xsd:boolean` and flag conflicting datatype declarations. The current exporter takes property names from its naming configuration. For example, it maps `https://data.hetarchief.be/ns/description/hasMissingAudioReels` to `https://data.hetarchief.be/ns/hasMissingAudioReels` through a configured name.

## Status legend

| Status | Meaning and migration action |
| --- | --- |
| MAP | Destination is sufficiently clear for a direct term replacement in the stated context. Preserve subject/object direction and literal values. |
| KEEP | Keep the same IRI. External or foundational vocabulary remains in use; linked classes and controlled values can still change. |
| CHANGE | Destination is clear, but apply the stated structural or value transformation. |
| REVIEW | **Uncertain mapping, unresolved conversion, or target-model conflict.** The stated destination is a candidate, not an instruction to transform blindly. |
| UNMAPPED | **No adequate supported destination identified.** Retain the original statement in a legacy/provenance graph until a decision is recorded. |

`M01`–`M17` refer to the decisions and transformation rules after the crosswalk. A MAP or KEEP row does not override a linked issue or the cross-cutting checks in the execution plan.

## Namespace key

Prefixes identify exact IRIs; spelling, case, `http`/`https` and trailing separators matter.

| Prefix | Namespace |
| --- | --- |
| `ha` | `https://data.hetarchief.be/ns/` |
| `haDes` | `https://data.hetarchief.be/ns/description/` |
| `haObj` | `https://data.hetarchief.be/ns/object/` |
| `haOrg` | `https://data.hetarchief.be/ns/organization/` |
| `haRig` | `https://data.hetarchief.be/ns/rights/` |
| `mh` | `https://data.hetarchief.be/ns/mediahaven/` |
| `schema` | `https://schema.org/` |
| `premis` | `http://www.loc.gov/premis/rdf/v3/` |
| `prov` | `http://www.w3.org/ns/prov#` |
| `odrl` | `http://www.w3.org/ns/odrl/2/` |
| `org` | `http://www.w3.org/ns/org#` |
| `dct` | `http://purl.org/dc/terms/` |
| `ebucore` | `http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#` |
| `edm` | `http://www.europeana.eu/schemas/edm/` |
| `bf` | `http://id.loc.gov/ontologies/bibframe/` |
| `foaf` | `http://xmlns.com/foaf/0.1/` |
| `rel` | `http://id.loc.gov/vocabulary/preservation/relationshipSubType/` |
| `evtAgRole` | `http://id.loc.gov/vocabulary/preservation/eventRelatedAgentRole/` |
| `evtObjRole` | `http://id.loc.gov/vocabulary/preservation/eventRelatedObjectRole/` |
| `evtOutcome` | `http://id.loc.gov/vocabulary/preservation/eventOutcome/` |
| `copyrightStatus` | `http://id.loc.gov/vocabulary/preservation/copyrightStatus/` |
| `skos` | `http://www.w3.org/2004/02/skos/core#` |
| `rdf` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` |
| `edtf` | `http://id.loc.gov/datatypes/edtf/` |

## Class crosswalk

These rows cover both shape targets and classes allowed as property values. Replace class IRIs in `rdf:type` assertions and relevant class references; this does not authorize changing resource instance IRIs.

### Legacy description classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haDes:2DArtwork` | `ha:TwoDimensionalArtwork` | **MAP** | D | — |
| `haDes:3DArtwork` | `ha:ThreeDimensionalArtwork` | **MAP** | D | — |
| `haDes:Audio` | `ha:Audio` | **MAP** | D | — |
| `haDes:AudioReel` | `ha:SoundReel` | **MAP** | D | Explicit rename in the target comment. |
| `haDes:AudiovisualCarrier` | `ha:AudiovisualCarrier` | **MAP** | D | — |
| `haDes:AudiovisualCarrierRepresentation` | `ha:AudiovisualCarrierRepresentation` | **MAP** | D | — |
| `haDes:DVD` | `ha:DVD` | **MAP** | D | — |
| `haDes:DVDChapter` | `ha:DVDChapter` | **MAP** | D | — |
| `haDes:Film` | `ha:Film` | **MAP** | D | — |
| `haDes:FilmCarrierRepresentation` | `ha:FilmCarrierRepresentation` | **MAP** | D | — |
| `haDes:Image` | `ha:Image` | **MAP** | D | — |
| `haDes:ImageReel` | `ha:ImageReel` | **MAP** | D | — |
| `haDes:MaterialArtwork` | `ha:MaterialArtwork` | **MAP** | D | — |
| `haDes:NewspaperIssue` | `ha:NewspaperIssue` | **MAP** | D | — |
| `haDes:NewspaperIssuePage` | `ha:NewspaperIssuePage` | **MAP** | D | — |
| `haDes:RoleName` | `ha:RoleType` | **MAP** | D | Controlled role concept; M02. |
| `haDes:SilentFilm` | `ha:SilentFilm` | **MAP** | D | — |
| `haDes:SoundFilm` | `ha:SoundFilm` | **MAP** | D | — |
| `haDes:Video` | `ha:Video` | **MAP** | D | — |
| `haDes:WrittenWorkCarrierRepresentation` | `ha:WrittenWorkCarrierRepresentation` | **MAP** | D | — |

### Legacy object classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haObj:CarrierRepresentation` | `ha:CarrierRepresentation` | **MAP** | D, O | — |
| `haObj:DigitalRepresentation` | `ha:DigitalRepresentation` | **MAP** | D, O, R | — |
| `haObj:FragmentRepresentation` | `ha:MediaFragment` | **MAP** | O | Preserve links to the intellectual entity and source file; M04. |
| `haObj:LocalIdentifier` | `ha:LocalIdentifier` | **MAP** | O | — |
| `haObj:PhysicalCarrier` | `ha:PhysicalCarrier` | **MAP** | D, O | — |
| `mh:Fragment` | `ha:MediahavenFragment` | **MAP** | O | — |
| `mh:Record` | `ha:MediahavenRecord` | **MAP** | O | — |

### Legacy organization and rights classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haOrg:ContentPartner` | `ha:ContentPartner` | **MAP** | D, G | — |
| `haOrg:DigitizationPartner` | `ha:DigitizationPartner` | **MAP** | G | — |
| `haOrg:EducationalPartner` | `ha:EducationalPartner` | **MAP** | G | — |
| `haOrg:Logo` | `ha:Logo` | **MAP** | G | — |
| `haOrg:OrganizationType` | `ha:OrganizationType` | **MAP** | G | — |
| `haOrg:ProjectPartner` | `ha:ProjectPartner` | **MAP** | G | — |
| `haOrg:ServiceConsumer` | `ha:ServiceConsumer` | **MAP** | G | — |
| `haOrg:ServiceProvider` | `ha:ServiceProvider` | **MAP** | G | — |
| `haRig:ContentRange` | `ha:ContentScope` | **MAP** | R | — |
| `haRig:MetadataRange` | `ha:MetadataScope` | **MAP** | R | - |
| `haRig:Motivation` | `ha:Motivation` | **MAP** | R | — |
| `haRig:UserGroup` | `ha:UserGroup` | **MAP** | R | — |

### External descriptive and organization classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `copyrightStatus:pub` | `ha:PublicDomainStatus` | **MAP** | R | - |
| `dct:FileFormat` | `ha:FileFormat` | **MAP** | O | — |
| `dct:RightsStatement` | `ha:RightsStatement` | **MAP** | R | — |
| `ebucore:Annotation` | `ha:Annotation` | **MAP** | D | — |
| `ebucore:ClosedCaptions` | `ha:ClosedSubtitling` | **MAP** | D | Accessibility captions and general subtitles must be distinguished; M08. |
| `ebucore:MediaFragment` | `ha:MediaFragment` | **MAP** | D | Covers spatial and temporal fragments; M04. |
| `ebucore:OpenCaptions` | `ha:OpenSubtitling` | **MAP** | D | Accessibility captions and general subtitles must be distinguished; M08. |
| `ebucore:TextAnnotation` | `ha:TextAnnotation` | **MAP** | D | — |
| `org:Organization` | `ha:Organization` | **MAP** | D, E, G | — |
| `org:OrganizationalUnit` | `ha:OrganizationalUnit` | **MAP** | G | — |
| `org:Post` | `ha:Post` | **MAP** | G | — |
| `org:Role` | `ha:RoleType` | **MAP** | G | - |
| `org:Site` | `ha:Site` | **MAP** | G | — |
| `schema:ArchiveComponent` | `ha:ArchiveComponent` | **MAP** | D | — |
| `schema:Brand` | `ha:Brand` | **MAP** | D, E | — |
| `schema:BroadcastEvent` | `ha:BroadcastEvent` | **MAP** | D | — |
| `schema:Collection` | `ha:Collection` | **MAP** | D | — |
| `schema:ContactPoint` | `ha:ContactPoint` | **MAP** | G | — |
| `schema:Country` | `ha:Country` | **MAP** | G | — |
| `schema:CreativeWork` | `premis:IntellectualEntity` (per resource) | **MAP** | D | - |
| `schema:CreativeWorkSeason` | `ha:Season` | **MAP** | D | — |
| `schema:CreativeWorkSeries` | `ha:Series` | **MAP** | D | — |
| `schema:Episode` | `ha:Episode` | **MAP** | D | — |
| `schema:Newspaper` | `ha:Newspaper` | **MAP** | D | — |
| `schema:PerformanceRole` | `ha:CastMemberEntry` | **MAP** | D | Preserve the cast entry and its performer link (M02). |
| `schema:Person` | `ha:Person` | **MAP** | D, E, G | — |
| `schema:Place` | `ha:Place` | **MAP** | D | — |
| `schema:PostalAddress` | `ha:PostalAddress` | **MAP** | G | — |
| `schema:QuantitativeValue` | `ha:QuantitativeValue` | **MAP** | D, O | — |
| `schema:Role` | `ha:Role` | **CHANGE** | D | Preserve role identity and move its agent link to rdf:value; M02. |
| `schema:Thing` | `ha:Thing` | **MAP** | D | — |
| `skos:Concept` | `skos:Concept` | **KEEP** | D, G, R | Used by the target model; preserve concept identities and SKOS descriptions. |

### External classes retained through imports

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `odrl:Action` | `odrl:Action` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Constraint` | `odrl:Constraint` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Permission` | `odrl:Permission` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Policy` | `odrl:Policy` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Prohibition` | `odrl:Prohibition` | **KEEP** | R | Retained in the imported external ontology. |
| `premis:Event` | `premis:Event` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:File` | `premis:File` | **KEEP** | D, O | Add `ha:MediaFile` to files with a qualifying MIME type; M04. |
| `premis:Fixity` | `premis:Fixity` | **KEEP** | O | Retained in the imported external ontology. |
| `premis:HardwareAgent` | `premis:HardwareAgent` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:IntellectualEntity` | `premis:IntellectualEntity` | **KEEP** | D, O, R | Retained in the imported external ontology. |
| `premis:License` | `premis:License` | **KEEP** | R | Retained in the imported external ontology. |
| `premis:Object` | `premis:Object` | **KEEP** | E, O | Retained in the imported external ontology. |
| `premis:OutcomeStatus` | `premis:OutcomeStatus` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:Representation` | `premis:Representation` | **KEEP** | D, O | Retained in the imported external ontology. |
| `premis:RightsStatus` | `premis:RightsStatus` | **KEEP** | R | Retained in the imported external ontology. |
| `premis:SoftwareAgent` | `premis:SoftwareAgent` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:StorageLocation` | `premis:StorageLocation` | **KEEP** | O | Retained in the imported external ontology. |
| `premis:StorageMedium` | `premis:StorageMedium` | **KEEP** | O | Retained in the imported external ontology. |
| `prov:Activity` | `prov:Activity` | **KEEP** | E | Retained in the imported external ontology. |

## Property crosswalk

Apply mappings by subject type and graph context. In particular, the same contribution property on a work and on a role wrapper has different migration actions. The source-file column identifies every shape file where the predicate occurs.

### Legacy description properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haDes:aspectRatio` | `ha:hasAspectRatio` | **MAP** | D | — |
| `haDes:audioNoiseReduction` | `ha:hasAudioNoiseReduction` | **MAP** | D | — |
| `haDes:audioRecordingSpeed` | `ha:hasAudioRecordingSpeed` | **REVIEW** | D | Preserve numeric measurement links after normalization. The variable-speed concept still needs a representation (M05). |
| `haDes:broadcastingOrganization` | `ha:hasBroadcastingOrganization` | **MAP** | D | — |
| `haDes:chapterNumber` | `ha:hasChapterNumber` | **MAP** | D | — |
| `haDes:coloringType` | `ha:hasFilmColorType` | **MAP** | D | — |
| `haDes:executor` | `ha:hasExecutor` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `haDes:hasMissingAudioReels` | `ha:hasMissingSoundReels` | **MAP** | D | Preserve xsd:boolean; the target range now agrees. |
| `haDes:hasMissingImageReels` | `ha:hasMissingImageReels` | **MAP** | D | Preserve xsd:boolean; the target range now agrees. |
| `haDes:iec60094Type` | `ha:hasIEC60094Type` | **MAP** | D | — |
| `haDes:licenseDistributor` | `ha:hasLicenseDistributor` | **REVIEW** | D | Persons/organizations fit ha:Agent; generic Thing values need classification; M02. |
| `haDes:numberOfAudioChannels` | `ha:hasNumberOfAudioChannels` | **MAP** | D | — |
| `haDes:numberOfAudioTracks` | `ha:hasNumberOfAudioTracks` | **MAP** | D | — |
| `haDes:numberOfMissingAudioReels` | `ha:hasNumberOfMissingSoundReels` | **MAP** | D | — |
| `haDes:numberOfMissingImageReels` | `ha:hasNumberOfMissingImageReels` | **MAP** | D | — |
| `haDes:numberOfPages` | `ha:hasNumberOfPages` | **MAP** | D | — |
| `haDes:numberOfReels` | `ha:hasNumberOfReels` | **MAP** | D | — |
| `haDes:owner` | `ha:hasOwner` | **REVIEW** | D | Target now ranges over ha:Agent; generic Thing values need classification; M02. |
| `haDes:pageNumber` | `ha:hasPageNumber` | **MAP** | D | — |

### Legacy object and Mediahaven properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haObj:hasAccessCopy` | `ha:hasAccessCopy` | **MAP** | O | — |
| `haObj:hasCarrierCopy` | `ha:hasCarrierRepresentation` | **MAP** | D, O | — |
| `haObj:hasFragmentRepresentation` | `ha:hasFragmentRepresentation` | **MAP** | O | Links the intellectual entity to its `ha:MediaFragment`; M04. |
| `haObj:hasIIIFCopy` | `ha:hasIIIFCopy` | **MAP** | O | — |
| `haObj:hasMasterCopy` | `ha:hasMasterCopy` | **MAP** | O | — |
| `haObj:hasMezzanineCopy` | `ha:hasMezzanineCopy` | **MAP** | O | — |
| `haObj:hasTranscriptionCopy` | `ha:hasTranscriptionCopy` | **MAP** | O | — |
| `haObj:isAccessCopyOf` | `ha:isAccessCopyOf` | **MAP** | O | Preserve representation-to-intellectual-entity direction; current target domain/range agree; M16. |
| `haObj:isCarrierCopyOf` | `ha:isCarrierRepresentationOf` | **MAP** | O | — |
| `haObj:isFragmentRepresentationOf` | `ha:isFragmentRepresentationOf` | **MAP** | O | Links the `ha:MediaFragment` to the intellectual entity it represents; M04. |
| `haObj:isIIIFCopyOf` | `ha:isIIIFCopyOf` | **MAP** | O | — |
| `haObj:isMasterCopyOf` | `ha:isMasterCopyOf` | **MAP** | O | — |
| `haObj:isMezzanineCopyOf` | `ha:isMezzanineCopyOf` | **MAP** | O | — |
| `haObj:isTranscriptionCopyOf` | `ha:isTranscriptionCopyOf` | **MAP** | O | — |
| `haObj:preservationProblem` | `ha:hasPreservationProblem` | **MAP** | D | — |
| `haObj:primaryIdentifier` | `ha:hasPrimaryLocalIdentifier` | **MAP** | O | Primary identifier node stays distinct from generic identifier links; M01. |
| `mh:record` | `ha:hasRecord` | **MAP** | O | — |
| `mh:tenantName` | `ha:hasTenantName` | **MAP** | G | — |

### Legacy organization and rights properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haOrg:hasAccountManager` | `ha:hasAccountManager` | **MAP** | G | — |
| `haOrg:hasLogo` | `ha:hasLogo` | **MAP** | G | — |
| `haOrg:hasPreference` | `ha:hasPreference` | **MAP** | G | — |
| `haOrg:isAccountManagerOf` | `ha:isAccountManagerOf` | **MAP** | G | — |
| `haOrg:requestForm` | `ha:hasContentRequestFormTemplate` | **MAP** | G | - |
| `haOrg:sector` | `ha:hasSector` | **MAP** | G | — |
| `haRig:isMotivatedBy` | `ha:isMotivatedBy` | **MAP** | R | — |

### External organization properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `org:classification` | `ha:hasClassification` | **MAP** | G | — |
| `org:hasPost` | `ha:hasPost` | **MAP** | G | — |
| `org:hasPrimarySite` | `ha:hasPrimarySite` | **MAP** | G | — |
| `org:hasSite` | `ha:hasSite` | **MAP** | G | — |
| `org:hasUnit` | `ha:hasUnit` | **MAP** | G | — |
| `org:holds` | `ha:holds` | **MAP** | G | — |
| `org:identifier` | `ha:hasIdentifier` | **MAP** | G | Preserve the source string (M01). |
| `org:postIn` | `ha:isPostIn` | **MAP** | G | — |
| `org:role` | `ha:hasRoleType` | **REVIEW** | G | Preserve the role-type concept. The target domain still needs a decision for posts (M02). |
| `org:siteAddress` | `ha:hasSiteAddress` | **MAP** | G | — |
| `org:siteOf` | `ha:isSiteOf` | **MAP** | G | — |
| `org:unitOf` | `ha:isUnitOf` | **MAP** | G | — |

### Schema.org properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `schema:about` | `ha:isAbout` | **MAP** | D | — |
| `schema:abstract` | `ha:hasAbstract` | **MAP** | D | Preserve language tags; target range now agrees. Undefined extra superproperty still needs cleanup; M07. |
| `schema:actor` | `ha:hasCastMember` | **CHANGE** | D | Link the work to the cast entry and move the performer link to `rdf:value` (M02). |
| `schema:addressCountry` | `ha:hasAddressCountry` | **REVIEW** | G | Preserve country nodes; resolve literal countries to entities; M12. |
| `schema:addressLocality` | `ha:hasAddressLocality` | **MAP** | G | — |
| `schema:addressRegion` | `ha:hasAddressRegion` | **MAP** | G | — |
| `schema:alternateName` | `ha:hasAlternateName` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:artMedium` | `ha:hasArtMedium` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:artform` | `ha:hasArtform` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:birthDate` | `ha:hasBirthDate` | **CHANGE** | G | Validate and retype the EDTF literal while preserving its lexical form (M06). |
| `schema:birthPlace` | `ha:hasBirthPlace` | **REVIEW** | G | Target now uses `ha:Place`. Resolving the source string still requires an approved policy (M12). |
| `schema:brand` | `ha:hasBrand` | **MAP** | D, E | — |
| `schema:caption` | `ha:hasCaptionText` | **REVIEW** | D | Target now uses `premis:File`. The source caption is on a digital representation (M08). |
| `schema:characterName` | `ha:hasCharacterName` | **MAP** | D | — |
| `schema:collectionSize` | `ha:hasCollectionSize` | **CHANGE** | D | Require nonnegative values; retype valid integers to xsd:nonNegativeInteger. |
| `schema:contactPoint` | `ha:hasContactPoint` | **MAP** | G | — |
| `schema:contactType` | `ha:hasContactType` | **MAP** | G | — |
| `schema:containedInPlace` | `ha:isContainedInPlace` | **MAP** | D | — |
| `schema:contributor` | `ha:hasContributor` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `schema:copyrightHolder` | `ha:hasRightsHolder` | **REVIEW** | D | Target ha:Agent excludes unidentified generic things unless classified; M02. |
| `schema:copyrightNotice` | No exact target (`ha:hasRights` is a broader candidate) | **UNMAPPED** | D | No dedicated notice predicate as no longer relevant. Replaced by broader rights classes. |
| `schema:copyrightYear` | `ha:hasCopyrightDate` | **UNMAPPED** | D | No longer relevant. |
| `schema:creator` | `ha:hasCreator` | **REVIEW** | D, O | Rename work-to-role links and use `rdf:value` for role-to-agent links (M02). The fixity domain now fits, but its source string still needs agent resolution (M13). |
| `schema:creditText` | `ha:hasCreditText` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:dateCreated` | `ha:hasCreationDate` | **REVIEW** | D, O | Normalize to `edtf:EDTF` where lossless. File and Mediahaven fragment subjects still fall outside the stated domain (M06). |
| `schema:dateDeleted` | `ha:hasDeletionDate` | **MAP** | O | Mediahaven fragment deletion timestamp; preserve xsd:dateTime. |
| `schema:dateModified` | `ha:hasModificationDate` | **MAP** | O | Mediahaven fragment modification timestamp; preserve xsd:dateTime. |
| `schema:datePublished` | `ha:hasPublicationDate` | **REVIEW** | D | Normalize level-specific literals to `edtf:EDTF`. Digital representation subjects still need a domain decision (M06). |
| `schema:deathDate` | `ha:hasDeathDate` | **CHANGE** | G | Validate and retype the EDTF literal while preserving its lexical form (M06). |
| `schema:deathPlace` | `ha:hasDeathPlace` | **REVIEW** | G | Source literal must become a resolved place entity; M12. |
| `schema:depth` | `ha:hasDepth` | **MAP** | D | — |
| `schema:description` | `ha:hasDescription` | **MAP** | D | — |
| `schema:duration` | `ha:hasDuration` | **MAP** | D, O | — |
| `schema:email` | `ha:hasEmail` | **MAP** | G | — |
| `schema:endDate` | `ha:hasEndDate` | **MAP** | D | Preserve `xsd:dateTime` on newspapers (M06). |
| `schema:endTime` | `ha:hasEndOffset` | **REVIEW** | D, O | xsd:time to integer seconds relative to media start; M04. |
| `schema:familyName` | `ha:hasFamilyName` | **MAP** | G | — |
| `schema:genre` | `ha:hasGenre` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:givenName` | `ha:hasGivenName` | **MAP** | G | — |
| `schema:hasPart` | `ha:hasPart` | **MAP** | D | — |
| `schema:height` | `ha:hasHeight` | **MAP** | D, O | Preserve measurement nodes; corrected domain union now includes files; M05. |
| `schema:identifier` | `ha:hasIdentifier` | **MAP** | D, O | Preserve the source string, including leading zeroes (M01). |
| `schema:inLanguage` | `ha:hasLanguage` | **REVIEW** | D | Validate/normalize xsd:language; representation/caption subjects exceed domain; M07. |
| `schema:instrument` | `ha:hasInstrument` | **MAP** | E | — |
| `schema:isPartOf` | `ha:isPartOf` | **REVIEW** | D | Most individual-to-collection links fit; source also uses collection subjects; M10. |
| `schema:issueNumber` | `ha:hasIssueNumber` | **REVIEW** | D | Source permits strings; target superproperty ha:hasPosition has an integer range; M10. |
| `schema:keywords` | `ha:hasKeywords` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:license` | `ha:hasLicense` | **MAP** | D | — |
| `schema:locationCreated` | `ha:hasCreationPlace` | **REVIEW** | D | Source uses a newspaper series; target domain is an intellectual entity; M10/M12. |
| `schema:logo` | `ha:hasLogo` | **MAP** | G | — |
| `schema:maintainer` | `ha:hasMaintainer` | **MAP** | D | — |
| `schema:material` | `ha:hasMaterial` | **MAP** | D | — |
| `schema:materialExtent` | `ha:hasMaterialExtent` | **MAP** | D | — |
| `schema:mentions` | `ha:mentions` | **MAP** | D | — |
| `schema:model` | `ha:hasModel` | **MAP** | E | Preserve `xsd:string` values on hardware and software agents (M13). |
| `schema:name` | `ha:hasName` | **REVIEW** | D, E, G | Language-tagged names map directly; plain-string country names still need a language policy; M07. |
| `schema:position` | `ha:hasPosition` | **MAP** | D | Preserve `xsd:integer`. The collection domain covers the mapped series (M10). |
| `schema:postOfficeBoxNumber` | `ha:hasPostOfficeBoxNumber` | **MAP** | G | — |
| `schema:postalCode` | `ha:hasPostalCode` | **MAP** | G | — |
| `schema:producer` | `ha:hasProducer` | **REVIEW** | D | Work-to-role fits; role-to-agent must use rdf:value; M02. |
| `schema:publisher` | `ha:hasPublisher` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `schema:roleName` | `ha:hasRoleType` | **MAP** | D | Preserve `xsd:string` names and concept IRIs. Apply the `ha:RoleType` class mapping to concepts (M02). |
| `schema:seasonNumber` | `ha:hasSeasonNumber` | **MAP** | D | Preserve `xsd:integer` on the mapped `ha:Season` (M10). |
| `schema:serialNumber` | `ha:hasSerialNumber` | **MAP** | E | Preserve the string under the dedicated serial-number predicate (M01). |
| `schema:spatial` | `ha:hasSpatial` | **MAP** | D | Keep the place IRI and apply the `ha:Place` class mapping (M12). |
| `schema:startDate` | `ha:hasStartDate` | **MAP** | D | Preserve `xsd:dateTime` on newspapers (M06). |
| `schema:startTime` | `ha:hasStartOffset` | **REVIEW** | D, O | xsd:time to integer seconds relative to media start; M04. |
| `schema:streetAddress` | `ha:hasStreetAddress` | **MAP** | G | — |
| `schema:telephone` | `ha:hasTelephone` | **MAP** | G | — |
| `schema:temporal` | `ha:hasTemporal` | **MAP** | D | Preserve language tags. The coverage superproperty now accommodates `rdf:langString` (M07). |
| `schema:thumbnailUrl` | `ha:hasThumbnailURL` | **CHANGE** | D | Source IRI becomes an xsd:anyURI literal if following the declared range; M07. |
| `schema:transcript` | `ha:hasTranscript` | **MAP** | D | Preserve the `xsd:string` on its digital representation (M08). |
| `schema:unitCode` | `ha:hasUnitCode` | **MAP** | D | — |
| `schema:unitText` | `ha:hasUnitText` | **MAP** | D | — |
| `schema:value` | `ha:hasMeasurementValue` | **MAP** | D | Only quantitative measurements map here; keep xsd:float; M05. |
| `schema:vatID` | `ha:hasVATID` | **MAP** | G | — |
| `schema:version` | `ha:hasVersion` | **MAP** | E | — |
| `schema:width` | `ha:hasWidth` | **MAP** | D, O | Preserve measurement nodes; corrected domain union now includes files; M05. |

### Dublin Core, BIBFRAME and FOAF properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `bf:edition` | `ha:hasEdition` | **MAP** | D | Preserve the concept IRI. Check publication-issue typing (M10/M11). |
| `bf:issuance` | `ha:hasIssuance` | **REVIEW** | D | Source means frequency; target means mode of issuance; M11. |
| `bf:precededBy` | `ha:isPrecededBy` | **REVIEW** | D | Source links newspaper series; target links publication issues; M10. |
| `bf:productionMethod` | `ha:hasProductionMethod` | **REVIEW** | D | Target range ha:BibframeProductionMethod is undefined; M11. |
| `bf:succeededBy` | `ha:isSucceededBy` | **MAP** | D | — |
| `bf:supplement` | `ha:hasSupplement` | **MAP** | D | — |
| `bf:supplementTo` | `ha:isSupplementTo` | **MAP** | D | — |
| `dct:available` | `ha:hasAvailabilityDate` | **CHANGE** | D | Convert `xsd:dateTime` to `edtf:EDTF` where time and offset can be preserved (M06). |
| `dct:description` | `ha:hasDescription` | **MAP** | G | — |
| `dct:format` | `ha:hasFormat` on files; class derivation on intellectual entities | **REVIEW** | D, O | File-format links now map directly; intellectual-entity strings still need classification; M03. |
| `dct:license` | `ha:hasLicense` | **REVIEW** | R | Digital-representation usage conflicts with target domain; M17. |
| `dct:rights` | `ha:hasRights` | **CHANGE** | D, R | Preserve both text and statement IRIs; do not conflate them; M14/M17. |
| `foaf:homepage` | `ha:hasHomepage` | **CHANGE** | G | Source IRI becomes an xsd:anyURI literal if following the declared range; M07. |

### EBUCore, ordering and preservation relationship properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `ebucore:annotationConfidence` | `ha:hasAnnotationConfidence` | **MAP** | D | — |
| `ebucore:annotationType` | `ha:hasAnnotationType` | **CHANGE** | D | Keep concept IRI; type the selected concept as ha:AnnotationType; M09. |
| `ebucore:hasAnnotationRelatedAgent` | `ha:hasAnnotationSubject` | **CHANGE** | D | Merge subject links while recording their original predicates; M09. |
| `ebucore:hasAnnotationRelatedArtefact` | `ha:hasAnnotationSubject` | **CHANGE** | D | Merge subject links while recording their original predicates; M09. |
| `ebucore:hasAnnotationTarget` | `ha:hasAnnotationTarget` | **MAP** | D | — |
| `ebucore:hasCaptioning` | `ha:hasSubtitling` | **MAP** | D | File/image-reel domains now fit; classify caption objects by purpose; M08. |
| `ebucore:hasCastMember` | `ha:hasCastMember` | **REVIEW** | D | Source string becomes a structured cast entry; identity cannot be inferred safely; M02. |
| `ebucore:hasMediaFragment` | `ha:hasMediaFragment` | **CHANGE** | D, O | Preserve direction and type the source file as `ha:MediaFile` once its MIME type qualifies; M04. |
| `ebucore:hasMimeType` | `ha:hasMimeType` | **MAP** | O | Preserve strings and use them to identify eligible media files; M03/M04. |
| `ebucore:hasObjectType` | `ha:hasObjectType` | **MAP** | D | — |
| `ebucore:height` | `ha:hasHeight` | **MAP** | D | Integer literal becomes a measurement node; unit depends on class context; M05. |
| `ebucore:isAnnotatedMediaResource` | `ha:annotatesMediaResource` | **MAP** | D | Preserve the annotation-to-fragment direction; the target also accepts `ha:MediaFile`; M04/M09. |
| `ebucore:isMediaFragmentOf` | `ha:isMediaFragmentOf` | **CHANGE** | D, O | Preserve direction and type the linked file as `ha:MediaFile` once its MIME type qualifies; M04. |
| `ebucore:regionDelimX` | `ha:hasRegionX` | **CHANGE** | D | Validate nonnegative pixel coordinates; reject negative or unknown-unit values; M05. |
| `ebucore:regionDelimY` | `ha:hasRegionY` | **CHANGE** | D | Corrected seeAlso now matches; validate nonnegative pixel coordinates as for X; M05. |
| `ebucore:synopsis` | `ha:hasSynopsis` | **MAP** | D | - |
| `ebucore:width` | `ha:hasWidth` | **MAP** | D | Integer literal becomes a measurement node; unit depends on class context; M05. |
| `edm:isNextInSequence` | `ha:immediatelyFollows` | **MAP** | O | Keep subject/object order: later resource to immediately preceding resource. |
| `evtAgRole:exe` | `ha:hasExecutingSoftware` | **MAP** | E | — |
| `evtAgRole:imp` | `ha:isImplementedBy` | **MAP** | E | Organization remains the implementer, retyped as ha:Organization. |
| `evtObjRole:out` | `ha:hasOutput` | **MAP** | E | Event to preservation object; preserve direction. |
| `evtObjRole:sou` | `ha:hasEventInput` | **MAP** | E | Event to input preservation object; preserve direction. |
| `rel:doc` | `ha:documents` | **MAP** | O | — |
| `rel:hsp` | `ha:hasStructuralPart` | **MAP** | D, O | — |
| `rel:hsr` | `ha:hasRenderingRoot` | **MAP** | O | — |
| `rel:hss` | `ha:hasDerivationSource` | **MAP** | O | — |
| `rel:inc` | `ha:includes` | **MAP** | O | — |
| `rel:isi` | `ha:isIncludedIn` | **MAP** | D, O | Keep direction, including the source DVD-chapter to DVD usage. |
| `rel:isp` | `ha:isStructuralPartOf` | **MAP** | D, O | — |
| `rel:isr` | `ha:isRepresentedBy` | **MAP** | O | — |
| `rel:rep` | `ha:represents` | **MAP** | O | — |
| `rel:sup` | `ha:supersedes` | **MAP** | O | — |

### ODRL, PREMIS, PROV, RDF and SKOS properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `odrl:action` | `odrl:action` | **KEEP** | R | Preserve the external predicate. |
| `odrl:constraint` | `odrl:constraint` | **KEEP** | R | Preserve the external predicate. |
| `odrl:hasPolicy` | `odrl:hasPolicy` | **KEEP** | R | Preserve the external predicate. |
| `odrl:leftOperand` | `odrl:leftOperand` | **KEEP** | R | Preserve the external predicate. |
| `odrl:operator` | `odrl:operator` | **KEEP** | R | Preserve the external predicate. |
| `odrl:permission` | `odrl:permission` | **KEEP** | R | Preserve the external predicate. |
| `odrl:prohibition` | `odrl:prohibition` | **KEEP** | R | Preserve the external predicate. |
| `odrl:rightOperand` | `odrl:rightOperand` | **KEEP** | R | Preserve the external predicate. |
| `odrl:target` | `odrl:target` | **KEEP** | R | Preserve the external predicate. |
| `premis:basis` | `premis:basis` | **KEEP** | R | Retain; retype rights-statement objects and review RightsBasis hierarchy; M17. |
| `premis:endDate` | `premis:endDate` | **KEEP** | R | Preserve the external predicate. |
| `premis:fixity` | `premis:fixity` | **KEEP** | O | Preserve the external predicate. |
| `premis:identifier` | `ha:hasLocalIdentifier` for local identifier nodes | **MAP** | O | Preserve the existing nodes. Keep `premis:identifier` for other PREMIS identifier usages (M01). |
| `premis:medium` | `premis:medium` | **KEEP** | O | Preserve the external predicate. |
| `premis:note` | `premis:note` | **KEEP** | E, R | Preserve the external predicate. |
| `premis:originalName` | `premis:originalName` | **KEEP** | O | Preserve the external predicate. |
| `premis:outcome` | `premis:outcome` | **KEEP** | E | Preserve the external predicate. |
| `premis:outcomeNote` | `premis:outcomeNote` | **KEEP** | E | Preserve the external predicate. |
| `premis:relationship` | `premis:relationship` | **KEEP** | O | Generic relationship remains generic; do not invent a specific relation subtype. |
| `premis:rightsStatus` | `premis:rightsStatus` | **KEEP** | R | Preserve status nodes; public-domain class/value distinction needs review; M17. |
| `premis:size` | `premis:size` | **KEEP** | O | Preserve the external predicate. |
| `premis:startDate` | `premis:startDate` | **KEEP** | R | Preserve the external predicate. |
| `premis:storedAt` | `premis:storedAt` | **KEEP** | D, O | Retain on carrier representations and files; retype linked carriers only. |
| `prov:endedAtTime` | `prov:endedAtTime` | **KEEP** | E | Preserve the external predicate. |
| `prov:generated` | `prov:generated` | **KEEP** | E | Keep on generic activities; ha:hasOutput is optional only for event-to-object links; M13. |
| `prov:startedAtTime` | `prov:startedAtTime` | **KEEP** | E | Preserve the external predicate. |
| `prov:wasAssociatedWith` | `prov:wasAssociatedWith` | **KEEP** | E | Preserve the external predicate. |
| `prov:wasDerivedFrom` | No supported target for the source usage | **UNMAPPED** | O | Absent from the target PROV extract; source points to Mediahaven metadata, not a preservation object; M13. |
| `prov:wasGeneratedBy` | `prov:wasGeneratedBy` | **KEEP** | E | Preserve the external predicate. |
| `rdf:value` | `rdf:value` | **KEEP** | O | Keep on fixity, storage locations and local identifiers; never rename globally; M01/M05. |
| `skos:altLabel` | `ha:hasAlternateName` on organizations | **MAP** | G | Context-specific name mapping; preserve language tags and keep SKOS labels on concepts; M07. |
| `skos:prefLabel` | `ha:hasName` on organizations; `skos:prefLabel` on concepts | **MAP** | G | Preserve language tags; role-type concept labels stay SKOS; M02/M07. |

## Decisions and transformation rules

The following model changes resolve migration findings. The REVIEW and UNMAPPED contexts below identify decisions still needed for the affected rules.

| Resolved finding | Effect on the plan |
| --- | --- |
| The model distinguishes `ha:hasIdentifier`, `ha:hasLocalIdentifier` and `ha:hasPrimaryLocalIdentifier`. | Keep identifier strings and reuse existing local identifier nodes and primary selections (M01). |
| `ha:hasCastMember` ranges over `ha:CastMemberEntry`. | Apply the work → cast entry → performer transformation in M02. |
| `ha:hasRoleType` accepts `ha:RoleType` resources and `xsd:string`. | Preserve both forms of legacy role names. Organizational posts still need a domain decision (M02). |
| `ha:hasFormat` now ranges over `ha:FileFormat`, and MIME type no longer inherits that range. | File-format links and MIME strings can migrate directly; intellectual-entity format classifications remain contextual (M03). |
| Width/height domains now include `premis:File`, and height uses `owl:unionOf`. | Existing measurement-node links can migrate directly; literal dimensions still require known units (M05). |
| `ha:hasRegionY` now references `ebucore:regionDelimY`. | Apply the same nonnegative-pixel conversion as for X (M05). |
| `ha:hasMeasurementValue` is a one-way subproperty of `rdf:value`. | No reverse measurement inference is declared; retain context-specific conversions (M05). |
| Creation, publication, availability, birth and death dates now range over `edtf:EDTF`. | Preserve date precision and uncertainty during datatype normalization. Creation and publication still have domain gaps (M06). |
| The nine text properties in M07 range over `rdf:langString`, and `ha:hasCoverage` has a union range for language-tagged text and resources. | Preserve language tags on temporal coverage and place IRIs on spatial coverage. Untagged names, synopsis and undefined `ha:description` still need attention (M07/M12). |
| Captioning and subtitling domains now include files and image reels. | The subject-domain blocker is resolved; caption purpose and object classification remain open (M08). |
| `ha:hasCaptionText` now uses the declared class `premis:File`. | The undefined class reference is resolved. Caption text on digital representations still needs a domain decision (M08). |
| `ha:hasTranscript` now has domain `ha:DigitalRepresentation`. | Keep transcript text on the representation that carries it (M08). |
| `ha:hasPosition` now includes collections in its domain, and `ha:hasEdition` accepts concept objects. | Preserve series positions and edition concept IRIs. The newspaper-issue hierarchy still needs a decision for validation (M10/M11). |
| `ha:hasBirthPlace` now ranges over `ha:Place`. | Use the same local class as for death places. Source strings still need place resolution (M12). |
| `ha:hasModel` has a domain covering hardware and software, and `ha:hasCreator` includes `premis:Fixity`. | Preserve model strings on both agent types. Fixity creator strings still require agent resolution (M13). |
| The inverse access-copy domain/range agree with source direction. | Preserve representation → intellectual entity edges (M16). |
| `ha:extended` and `ha:limited` now have type `ha:MetadataScope`. | Map these controlled values directly; other ODRL typing questions remain open (M17). |

### M01 — Separate literal identifiers, local identifier nodes and primary identifiers

The target defines distinct properties for the three source patterns (`hetarchief/model.rdfs.ttl:1474` and `hetarchief/model.rdfs.ttl:2514`).

- Map string-valued `schema:identifier` and `org:identifier` to `ha:hasIdentifier`. Preserve the exact strings, including leading zeroes. Map serial numbers to `ha:hasSerialNumber`, which has the same `xsd:string` range as its superproperty `ha:hasIdentifier`.
- Map `premis:identifier` links from intellectual entities to existing `haObj:LocalIdentifier` nodes to `ha:hasLocalIdentifier`. Retype the nodes to `ha:LocalIdentifier` and keep their identities and `rdf:value` strings. Retain `premis:identifier` links outside this local-identifier context.
- Map `haObj:primaryIdentifier` to `ha:hasPrimaryLocalIdentifier` and preserve the explicitly selected node. Keep both links when the source includes a local identifier link and a primary selection for the same node.

Both object-valued target properties are subproperties of `premis:identifier`. For consumers that query explicit triples, update the query paths or materialize the PREMIS superproperty links. Preserve identifiers independently when their strings match across systems. Keep `rdf:value` on checksums and storage locations as well (M05).

### M02 — Preserve contribution roles and distinguish role assignments from role types

The source repeats contribution predicates on two levels: `work → role → agent` (`description/description.shacl.ttl:140` and `description/description.shacl.ttl:1837`). A global predicate replacement would make the role node another work or intellectual entity through the target domains.

For a contextual contribution:

1. Preserve the existing role node's identity and map its class to `ha:Role`, using `ha:CastMemberEntry` for cast credits.
2. Rename the incoming work predicate to `ha:hasCreator`, `ha:hasContributor`, `ha:hasPublisher`, `ha:hasProducer`, `ha:hasCastMember` or `ha:hasExecutor`, as appropriate.
3. Replace the role's outgoing `schema:creator`, `schema:contributor`, `schema:publisher`, `schema:producer`, `schema:actor` or `haDes:executor` agent link with `rdf:value`. The `ha:Role` restriction now calls for an `rdf:value` pointing to an `ha:Agent` (`hetarchief/model.rdfs.ttl:560`).
4. Preserve `schema:characterName` as `ha:hasCharacterName`. Map `schema:roleName` to `ha:hasRoleType` and preserve both `xsd:string` literals and concept IRIs. Retype `haDes:RoleName` concepts as `ha:RoleType` (`hetarchief/model.rdfs.ttl:1548`).

For example, subject to the role decisions below, this preserves a creator assignment:

```turtle
# Before
:work schema:creator :credit .
:credit a schema:Role ;
    schema:creator :person ;
    schema:roleName :director .

# After
:work ha:hasCreator :credit .
:credit a ha:Role ;
    rdf:value :person ;
    ha:hasRoleType :director .
:director a ha:RoleType .
```

**REVIEW:** the source permits generic `schema:Thing` resources for role agents, owners and license distributors. The role restriction and the target ranges for `ha:hasOwner` and `ha:hasLicenseDistributor` use `ha:Agent`. `ha:Person` and `ha:Organization` qualify through the class hierarchy. Generic things still need an agreed agent-typing policy. Preserve the source links for unresolved agents.

Map the `schema:actor` work-to-role link to `ha:hasCastMember` and type the role as `ha:CastMemberEntry`. Preserve cast order as `ha:hasPosition`, the character name as `ha:hasCharacterName`, and the performer link as `rdf:value`. **REVIEW:** preserve source `ebucore:hasCastMember` text until a reliable structured entry can be produced.

For organizational functions, `org:Role` means an abstract SKOS concept (`ontologies/org.rdfs.ttl:45`). Preserve concept IRIs and `skos:prefLabel` when mapping them to `ha:RoleType`. **REVIEW:** `org:role` links a post to that concept, while `ha:hasRoleType` has domain `ha:Role`. The post hierarchy uses `rdf:subClassOf` (`hetarchief/model.rdfs.ttl:483`). Confirm how the property should apply to posts, including vacant posts, given the `ha:Role` agent restriction.

### M03 — Split the two uses of dct:format

On files, source `dct:format` points to a `dct:FileFormat` resource. Preserve its IRI and retype it to `ha:FileFormat`, which the model declares equivalent to `dct:FileFormat`. Map the predicate directly to `ha:hasFormat`, whose range is now `ha:FileFormat` (`hetarchief/model.rdfs.ttl:2495`).

On intellectual entities, `dct:format` is one of nine strings (`description/description.shacl.ttl:464`). These are content classifications, not file-format entities. The following are candidate class derivations, not blanket replacements of the format value:

| Source string | Candidate target treatment | Confidence / limitation |
| --- | --- | --- |
| `audio` | Add `rdf:type ha:Audio` | Clear content-class candidate. |
| `video` | Add `rdf:type ha:Video` | Clear content-class candidate. |
| `film` | Add `rdf:type ha:Film` | Clear content-class candidate. |
| `image` | Add `rdf:type ha:Image` | Clear content-class candidate. |
| `paper` | Add `ha:NewspaperIssue` | beware: paper material does not by itself establish NewspaperIssue semantics. |
| `newspaper` | Add `ha:NewspaperIssue` | Beware: distinguish an individual issue from the newspaper series. |
| `newspaperpage` | Add `rdf:type ha:NewspaperIssuePage` | Strong candidate; check parent-issue links. |
| `videofragment` | Classify the intellectual content and model its fragment representation separately | **REVIEW:** no dedicated target video-fragment intellectual-entity class. |
| `audiofragment` | Classify the intellectual content and model its fragment representation separately | **REVIEW:** no dedicated target audio-fragment intellectual-entity class. |

Keep the original classification in the migration provenance until its disposition is approved. Do not replace these strings with `ha:FileFormat` instances or turn an intellectual entity into a representation solely because its format says “fragment”.

Map `ebucore:hasMimeType → ha:hasMimeType` directly and preserve its string values. The target no longer makes this a subproperty of `ha:hasFormat`, so MIME strings no longer inherit the file-format class range.

### M04 — Migrate media files and fragments and convert fragment offsets

Map `haObj:FragmentRepresentation` and `ebucore:MediaFragment` to `ha:MediaFragment`, preserving instance IRIs. Apply the same type replacement to any records already migrated as `ha:FragmentRepresentation`. Keep `ha:isFragmentRepresentationOf` and `ha:hasFragmentRepresentation` where present to express which `premis:IntellectualEntity` the fragment represents. A fragment may describe a spatial region, a temporal segment, or both. Base any `ha:DigitalRepresentation` type on independent evidence.

Add an explicit `rdf:type ha:MediaFile` to each `premis:File` with a `ha:hasMimeType` string beginning with `audio/`, `video/` or `image/` and a nonempty subtype. For previously migrated records, replace `ha:MediaResource` with `ha:MediaFile` on qualifying files and with `ha:MediaFragment` on identified fragments. Flag unresolved resource types and files with missing or nonqualifying MIME values when a media file is required, and retain the source statements in migration provenance.

Preserve the direction of both source-file links. `ha:hasMediaFragment` goes from the media file to the fragment, and `ha:isMediaFragmentOf` goes from the fragment to the media file. `ha:annotatesMediaResource` goes from the annotation to a `ha:MediaFile` or `ha:MediaFragment` (M09).

The source uses `schema:startTime` and `schema:endTime` as `xsd:time` on both legacy fragment classes. Map them to `ha:hasStartOffset` and `ha:hasEndOffset` as **integer seconds relative to the start of the source media**. The target shape allows spatial fragments without offsets.

Once the source values are confirmed to be relative offsets, convert `HH:MM:SS` to `3600 × HH + 60 × MM + SS`; for example, `00:01:30` becomes `90`. **REVIEW:** fractional seconds, time zones, wall-clock values and wrapped times cannot be converted safely under that integer model without additional decisions. Do not round silently or manufacture a media-start reference. Keep `schema:duration → ha:hasDuration` as `xsd:duration`.

### M05 — Preserve measurement structure and units

Existing `schema:QuantitativeValue` nodes become `ha:QuantitativeValue`. Map `schema:value` to `ha:hasMeasurementValue`, and rename the unit predicates to `ha:hasUnitCode` and `ha:hasUnitText`. Keep unit codes and numeric precision; do not recalculate measurements merely to rename predicates.

`ebucore:width` and `ebucore:height` are integer literals on source media fragments. Their target properties expect measurement nodes. **REVIEW:** create a measurement node only when its unit is known from the data or authoritative context; the source descriptions allow pixels or physical dimensions. The new node must preserve the original value and use the approved unit. Source file-level width/height links already point to measurement nodes and need no such wrapping.

The target width/height domain unions now include `premis:File`, and `ha:hasHeight` uses the corrected `owl:unionOf` (`hetarchief/model.rdfs.ttl:1139` and `hetarchief/model.rdfs.ttl:1739`). These declaration blockers are resolved: existing source file-level measurement-node links can migrate directly.

For region coordinates, validate that values are nonnegative and measured in pixels before emitting `ha:hasRegionX` / `ha:hasRegionY`. The Y property's corrected `seeAlso` now points to the actual source `ebucore:regionDelimY`; both coordinates use the same conversion checks.

For audio speed, preserve existing `/id/rotational-speed/` IRIs. The supporting SKOS file uses `http://schema.org/QualitativeValue`, whereas the shape requires `https://schema.org/QuantitativeValue`. Numeric entries carry usable value/unit facts and can be normalized deliberately. **REVIEW:** the `variable` concept has no numeric measurement, so do not invent a float or treat it as an ordinary quantitative value.

Finally, `ha:hasMeasurementValue` is declared `rdfs:subPropertyOf rdf:value`, without a global equivalence (`hetarchief/model.rdfs.ttl:1600`). This permits measurement values to entail generic RDF values without turning unrelated RDF values into measurements. Keep `rdf:value` on identifiers, checksums, storage locations and role-agent links; map only quantitative-value contexts to `ha:hasMeasurementValue`.

### M06 — Preserve date precision

| Source usage | Target | Required treatment |
| --- | --- | --- |
| `schema:dateCreated` with EDTF levels 0/1/2 or `xsd:dateTime` | `ha:hasCreationDate` with `edtf:EDTF` | Normalize valid EDTF literals and convert timestamps where lossless. **REVIEW** for file and Mediahaven fragment subjects. |
| `schema:datePublished` with EDTF levels 0/1/2 | `ha:hasPublicationDate` with `edtf:EDTF` | Normalize valid EDTF literals. **REVIEW** for digital representation subjects. |
| `schema:copyrightYear`: integer | `ha:hasCopyrightDate`: `xsd:dateTime` | **REVIEW:** a year does not identify a day or time. A model change or a separate year representation is required. |
| `dct:available` with `xsd:dateTime` | `ha:hasAvailabilityDate` with `edtf:EDTF` | Convert where lossless and retain the original timestamp for review if the accepted format cannot express its time, fractional precision or offset. |
| `schema:birthDate` and `schema:deathDate` with EDTF level 1 | `ha:hasBirthDate` and `ha:hasDeathDate` with `edtf:EDTF` | Retype valid literals and preserve their lexical form and date uncertainty. |
| `schema:startDate`, `schema:endDate` on newspapers | `ha:hasStartDate`, `ha:hasEndDate`: `xsd:dateTime` | Rename and preserve the literal. |
| Mediahaven `schema:dateDeleted`, `schema:dateModified` | `ha:hasDeletionDate`, `ha:hasModificationDate`: `xsd:dateTime` | Rename and preserve the timestamp. |
| Rights `premis:startDate`, `premis:endDate` | Same predicates | Keep the source `xsd:dateTime` literals. |

The common `edtf:EDTF` range removes the old level-1 restriction and the need to turn descriptive creation dates into timestamps. Validate the source lexical form against the accepted EDTF profile before changing the datatype IRI. Preserve valid partial dates, intervals and uncertainty. For timestamps, require a lossless representation of the original precision and offset. See the timestamp examples in the [Library of Congress EDTF specification](https://www.loc.gov/standards/datetime/edtf.html).

The creation-date domain still omits files and Mediahaven fragments, and the publication-date domain still omits digital representations. Resolve those domain gaps on the original subjects. The draft target shapes still check level-specific EDTF datatype IRIs and require `xsd:dateTime` for availability. Align those checks with the chosen EDTF datatype before validating migrated dates. See `description/description.shacl.ttl:107`, `objects/objects.shacl.ttl:1125` and `hetarchief/model.shacl.ttl:1094`.

### M07 — Preserve multilingual text, language codes and URI node kinds

Most source `schema:name` values, organization `skos:prefLabel` / `skos:altLabel`, and descriptive fields are `rdf:langString`. The target ranges for `ha:hasName`, `ha:hasAlternateName`, `ha:hasAbstract`, `ha:hasGenre`, `ha:hasKeywords`, `ha:hasTemporal`, `ha:hasArtform`, `ha:hasArtMedium` and `ha:hasCreditText` are now `rdf:langString`, matching `ha:hasDescription`. Preserve all language tags during direct predicate mappings. The former direct-range conflicts are resolved; the remaining exceptions are described below.

For organization labels, map `skos:prefLabel` to `ha:hasName` and `skos:altLabel` to `ha:hasAlternateName` in that context, preserving every language-tagged value. This follows their naming function and compatible target ranges; the target does not assert a global equivalence with the SKOS predicates. Keep SKOS labels on concepts, especially `ha:RoleType`, rather than renaming all occurrences globally.

**REVIEW:** source country names are `xsd:string` (`organizations/organizations.shacl.ttl:975`), so those `schema:name` values do not directly fit the new `ha:hasName` range. Add a language tag only when supported by evidence, or agree another representation; never guess the language from the country's identity. Other observed untagged names need the same check.

Map temporal coverage directly and preserve its language tags. `ha:hasCoverage` now has a range of `rdf:langString` or `ha:Thing`, which also accommodates spatial coverage resources (M12).

**REVIEW** remains for `ha:hasSynopsis`, which ranges over `xsd:string` while its superproperty `ha:hasDescription` ranges over `rdf:langString`. The abstract and description ranges now agree. `ha:hasAbstract` and imported PREMIS notes still reference the undefined `ha:description`, which needs a definition or removal from the model.

`schema:inLanguage` strings become `ha:hasLanguage` with `xsd:language`; validate the lexical form and normalize only with evidence. The target domain is an intellectual entity, while source usage also covers digital representations and open captions. Resolve that domain mismatch.

Source `foaf:homepage` and `schema:thumbnailUrl` values are IRIs, while their target ranges are `xsd:anyURI`. If the target's literal representation is retained, convert the exact IRI string to an `xsd:anyURI` literal and update consumers accordingly. If links should remain RDF resources, the target ranges need adjustment instead. Do not silently mix the two representations.

### M08 — Distinguish captioning, subtitles, caption text and transcripts

The source uses `ebucore:hasCaptioning` for files and image reels, allowing a file or closed-caption object in the former case and open captions in the latter. The target separates accessibility captions (`ha:Captioning`, `ha:ClosedCaptions`, `ha:OpenCaptions`) from general subtitles (`ha:Subtitling`, `ha:ClosedSubtitling`, `ha:OpenSubtitling`). Its comments explicitly leave the replacement question open (`hetarchief/model.rdfs.ttl:126`).

**REVIEW:** classify each existing caption object by actual purpose; do not assume all subtitles are accessibility captions. Choose the matching `ha:hasCaptioning` or `ha:hasSubtitling` link. A detached subtitle file can be `ha:ClosedSubtitling` only when its role is established. Both link properties now have domain unions covering `premis:File` and `ha:ImageReel`, resolving the image-reel subject mismatch. An otherwise unclassified file object still needs a justified captioning/subtitling type.

Map `schema:transcript` directly to `ha:hasTranscript`. Its domain is now `ha:DigitalRepresentation`, so the source `xsd:string` stays on the same representation.

**REVIEW:** the domain of `ha:hasCaptionText` is now `premis:File` (`hetarchief/model.rdfs.ttl:895`), while `schema:caption` describes a digital representation (`description/description.shacl.ttl:834`). Preserve the caption on the legacy representation until the target can express representation-level caption text or there is evidence that it applies to a specific file.

### M09 — Merge annotation subjects while retaining provenance

Map both `ebucore:hasAnnotationRelatedArtefact` and `ebucore:hasAnnotationRelatedAgent` to `ha:hasAnnotationSubject`, keeping the referenced resource IRIs. The source permits one artefact and an additional agent; retain both when they differ. When both old predicates have the same object, RDF deduplication will leave one target triple. Record the original predicates in migration provenance if their distinction is needed.

Retype only concepts actually used as `ebucore:annotationType` values to `ha:AnnotationType`. Preserve `ebucore:annotationConfidence → ha:hasAnnotationConfidence` as a decimal. Map `ebucore:isAnnotatedMediaResource` to `ha:annotatesMediaResource`, keeping the annotation as the subject and the annotated fragment or qualifying media file as the object (M04). Preserve the separate target file link as `ha:hasAnnotationTarget`.

### M10 — Keep grouping, structural membership and publication sequencing distinct

`schema:CreativeWork` appears as a permitted value class but has no single corresponding generic class in the target. Existing explicit series, season, collection, archive-component and newspaper types have the tabled destinations. **REVIEW:** a resource known only as `schema:CreativeWork` must be classified as a grouping or an individual intellectual work before a replacement class is chosen.

Keep the source distinction between generic `schema:hasPart` / `schema:isPartOf` and PREMIS structural relationships `rel:hsp` / `rel:isp`. They map to `ha:hasPart` / `ha:isPartOf` and `ha:hasStructuralPart` / `ha:isStructuralPartOf`, respectively. Cross-category preservation inclusion uses `ha:includes` / `ha:isIncludedIn`. Do not collapse these relationships.

The `ha:hasPosition` domain now includes `ha:Collection`, which covers the mapped `ha:Series` subjects. Map their integer positions directly. Map integer season numbers directly to `ha:hasSeasonNumber` on `ha:Season`. **REVIEW** remains for `ha:isPartOf`, whose domain only covers intellectual entities while source series, seasons and archive components also use it. Resolve how to represent membership on those collections.

The source `bf:precededBy` links newspaper series; target `ha:isPrecededBy` links `ha:PublicationIssue` instances. **REVIEW:** this is not a safe series-level rename, even though the target references the same external predicate. In contrast, `bf:succeededBy`, `bf:supplement` and `bf:supplementTo` have target newspaper-to-newspaper definitions matching the source context.

`ha:hasIssueNumber` has no direct range, but its superproperty `ha:hasPosition` ranges over integers; the source allows strings such as numbered or alphanumeric designations. Preserve the string and resolve the inherited range. The target also does not explicitly make `ha:NewspaperIssue` a subclass of `ha:PublicationIssue`, although issuance/edition/issue-number domains use the latter. Decide the intended hierarchy or explicit dual typing before validation.

For `edm:isNextInSequence → ha:immediatelyFollows`, preserve direction: **the subject follows the object**. This agrees with the legacy EDM definition (`ontologies/edm.rdfs.ttl:12`); do not reverse the edge based on the English name alone.

### M11 — Resolve production method, edition and issuance semantics

The `bf:productionMethod → ha:hasProductionMethod` candidate is clear, but its target range is undefined `ha:BibframeProductionMethod`. The declared concept class is `ha:ProductionMethod` (`hetarchief/model.rdfs.ttl:1502` and `hetarchief/model.rdfs.ttl:1896`). **REVIEW:** settle the range, then retain the existing production-method concept IRIs and add the agreed target type.

Map `bf:edition` to `ha:hasEdition` and preserve the edition-type concept IRIs. The target retains `skos:Concept` as the range and has removed the datatype-property declaration. Apply the publication-issue typing check in M10.

Source `bf:issuance` describes publication frequency, such as daily or weekly (`description/description.shacl.ttl:1140`). The target `ha:hasIssuance` still describes mode of issuance, such as whether a publication ends or is updated in parts. Its TODO records the intended change to frequency (`hetarchief/model.rdfs.ttl:1174`). **REVIEW** the source concepts and preserve frequency statements pending that change. Only genuine mode-of-issuance values fit the current target definition.

### M12 — Resolve literal places and countries without guessing identity

Source birth/death places are strings, whereas target properties expect place resources. Address country can be a string or a `schema:Country` resource. Keep existing resource identities and apply the class mappings; resolve strings through an approved place/country authority or a documented local-node policy, preserving their original text. Do not merge ambiguous place names merely because they match lexically.

Birth, death and creation places now share the `ha:Place` range. Map `schema:spatial` links directly and preserve each place IRI, since `ha:Place` is a subclass of `ha:Thing` and the `ha:hasCoverage` union range includes `ha:Thing`. **REVIEW** remains for resolving source birth/death place strings and for the creation-place domain on newspaper series (M10).

### M13 — Preserve generic provenance and hardware/software agent distinctions

`prov:wasDerivedFrom` is used from intellectual entities, representations and files to `mh:Fragment` metadata records (`objects/objects.shacl.ttl:304`). That predicate is not defined in the supplied target PROV extract. `ha:hasDerivationSource` is not a safe substitute: it links preservation objects to preservation objects, while `ha:MediahavenFragment` describes the metadata-system fragment. The target itself raises the question of a generic derivation property (`hetarchief/model.rdfs.ttl:1462`). **UNMAPPED:** preserve these provenance links until the model explicitly retains/imports the PROV property or defines a suitable alternative. The Mediahaven fragment class and its record relation can migrate independently.

Keep `prov:generated` on generic `prov:Activity` instances. Only an established preservation-event-to-object link is eligible for the more specific `ha:hasOutput`; the original `evtObjRole:out` already maps there directly. Do not narrow arbitrary generated IRIs to preservation objects.

The source also uses `schema:creator` as a string on `premis:Fixity` (`objects/objects.shacl.ttl:1003`). `ha:hasCreator` now includes fixity subjects, and the range still requires a person, organization or role. **REVIEW** whether the string can be resolved to a qualifying resource under an approved attribution rule. Keep the original value in the legacy graph when agent resolution is unavailable.

Map `schema:model` directly to `ha:hasModel` for both hardware and software agents. Its `xsd:string` range and union domain match the shared source model property (`hetarchief/model.rdfs.ttl:1303` and `events/events.shacl.ttl:282`).

### M14 — Preserve copyright notices separately from general rights text

No dedicated target equivalent of `schema:copyrightNotice` was identified. `ha:hasRights` is a possible broader container, but combining notices with general source `dct:rights` text loses the distinction. **UNMAPPED:** preserve notices under their original predicate pending a decision to keep an external notice term, add a dedicated target term, or explicitly accept a broader mapping with provenance.

`dct:rights → ha:hasRights` itself is supported. In D it carries text; in R it points to a rights-statement resource. Preserve the RDF node kind and both values when both exist. Do not stringify statement IRIs or replace free text with an arbitrary controlled statement.

### M15 — Review request-form links versus templates

`haOrg:requestForm` describes a string containing the URL of a request form. `ha:hasContentRequestFormTemplate` explicitly describes a URI template whose placeholders are replaced with content-specific values. **REVIEW:** a plain URL may be usable as a constant template, but that behavior must be confirmed in the application. Preserve existing placeholders verbatim where present; do not invent item parameters. Evidence: `organizations/organizations.rdfs.ttl:144` and `hetarchief/model.rdfs.ttl:1542`.

### M16 — Preserve inverse access-copy direction

Map `haObj:isAccessCopyOf` directly to `ha:isAccessCopyOf`: digital representation → intellectual entity. The current workspace target declares domain `ha:DigitalRepresentation`, range `premis:IntellectualEntity`, and inverse `ha:hasAccessCopy` (`hetarchief/model.rdfs.ttl:2128`), which agree with this direction. Preserve the source edge; check its inverse against the corresponding intellectual-entity-to-representation link.

### M17 — Migrate rights values as well as predicates

Keep the ODRL graph structure: policy → permission/prohibition → action/constraint, constraint → left operand/operator/right operand, and policy → target. Keeping ODRL predicates does not mean keeping all operand IRIs. Apply the exact value crosswalk in the next section, including occurrences in reusable permission vocabularies.

`ha:extended` and `ha:limited` now have the declared type `ha:MetadataScope`, resolving their target typing blocker. Map both controlled-value IRIs directly. Source `sh:in` still permits action concepts as right operands while its `sh:class` alternatives only cover user groups and metadata/content scopes. **REVIEW:** settle those allowed-value/type combinations and the target ODRL extract's datatype-property declaration for IRI-valued `odrl:rightOperand`; do not carry over inconsistent constraints blindly.

The source uses `copyrightStatus:pub` in `sh:class`; the target explicitly equates it with class `ha:PublicDomainStatus`. That supports a class mapping, but does not make a target class IRI a rights-status instance. **REVIEW:** distinguish existing status nodes typed with the source class from direct vocabulary-value objects. A direct public-domain value may require a status node typed `ha:PublicDomainStatus`; do not emit `premis:rightsStatus ha:PublicDomainStatus` as a shortcut.

Retype `dct:RightsStatement` resources to `ha:RightsStatement`, preserving their IRIs and SKOS data. Keep `premis:License`, `premis:RightsStatus`, `premis:basis`, `premis:note`, `premis:startDate` and `premis:endDate`. The target `premis:basis` ranges over `premis:RightsBasis`, but the supplied definitions do not connect `ha:RightsStatement` or `premis:License` to that superclass; establish an agreed hierarchy or typing policy. The target `ha:hasLicense` has an intellectual-entity domain, although source `dct:license` also occurs on digital representations. Do not move a representation's license to its intellectual entity automatically.

The target makes `ha:hasLicense` equivalent to `ha:hasAccessRights`; do not use that declaration as a reason to collapse license information, access policies and rights-status records during data conversion.

## Controlled-value crosswalk

These values occur directly in the source shapes' active `sh:in` lists. They are data resources, not new class/property counts. Apply their mappings in object positions and wherever those same vocabulary resources are described or referenced; do not perform a blanket namespace replacement on unrelated instance IRIs.

### Rights operands, actions and event outcomes

| Source value | Target value | Status / note |
| --- | --- | --- |
| `haRig:metadataRange` | `ha:metadataScopeOperand` | MAP; left operand, distinct from the scope class. |
| `haRig:contentRange` | `ha:contentScopeOperand` | MAP; left operand, distinct from the scope class. |
| `haRig:extended` | `ha:extended` | MAP; target now types it as `ha:MetadataScope`; M17. |
| `haRig:limited` | `ha:limited` | MAP; target now types it as `ha:MetadataScope`; M17. |
| `haRig:full` | `ha:full` | MAP. |
| `haRig:partial` | `ha:partial` | MAP. |
| `haRig:available-for-consultation` | `ha:available-for-consultation` | MAP; action; review source right-operand usage separately. |
| `haRig:downloadable` | `ha:downloadable` | MAP; action; review source right-operand usage separately. |
| `haRig:between-partners` | `ha:between-partners` | MAP. |
| `haRig:educational-public` | `ha:educational-public` | MAP. |
| `haRig:intra-muros` | `ha:intra-muros` | MAP. |
| `haRig:public` | `ha:public` | MAP. |
| `haRig:research-public` | `ha:research-public` | MAP. |
| `odrl:eq` | `odrl:eq` | KEEP; imported operator. |
| `odrl:lt` | `odrl:lt` | KEEP; imported operator. |
| `odrl:recipient` | `odrl:recipient` | KEEP; imported left operand. |
| `odrl:dateTime` | `odrl:dateTime` | KEEP; imported left operand. |
| `odrl:absoluteTemporalPosition` | `odrl:absoluteTemporalPosition` | KEEP; imported left operand. |
| `evtOutcome:fai` | `ha:fail` | CHANGE; target does not explicitly type it as `premis:OutcomeStatus`; add agreed type or resolve vocabulary typing. |
| `evtOutcome:suc` | `ha:success` | CHANGE; same outcome-status typing issue. |
| `evtOutcome:war` | `ha:warning` | CHANGE; same outcome-status typing issue. |

The three event outcome candidates have matching target `seeAlso` references and definitions. Preserve their intended `premis:OutcomeStatus` role, rather than changing `premis:outcome` to a literal success flag.

### Other enumerations and stable concept identities

| Source values | Migration action | Status / note |
| --- | --- | --- |
| `https://data.hetarchief.be/id/iec60094-type/` with local names `I`, `II`, `III`, `IV` | Keep all four IRIs under `ha:hasIEC60094Type`. | KEEP; retain SKOS labels and scheme. |
| `https://data.hetarchief.be/id/rotational-speed/` with local names `variable`, `16-rpm`, `19-cm-s`, `2.375-cm-s`, `33-1-3-rpm`, `38-cm-s`, `4.75-cm-s`, `72-cm-s`, `78-rpm`, `90-rpm`, `9.5-cm-s` | Keep all eleven concept IRIs. Map numeric speed links to `ha:hasAudioRecordingSpeed` after normalizing their measurements. Preserve links to `variable` in the legacy graph pending a representation decision. | REVIEW (M05). |
| `"DBX"`, `"Dolby A"`, `"Dolby B"`, `"Dolby C"`, `"Dolby D"` | Keep the five string values under `ha:hasAudioNoiseReduction`. | KEEP. |
| `https://data.hetarchief.be/id/edition-type/` with local names `morning-edition`, `afternoon-edition`, `evening-edition`, `weekend-edition` | Keep all four concept IRIs under `ha:hasEdition`. | MAP (M10/M11). |
| `https://data.hetarchief.be/id/production-method/` with local names `handwritten`, `typed`, `printed` | Keep all three concept IRIs; add the agreed production-method type. | REVIEW; undefined target range; M11. |
| `https://data.hetarchief.be/id/color-type/` with local names `BandW`, `Color`, `Colorized`, `Composite`, `Tinted`, `Toned`, `UnknownColorType` | Keep all seven IRIs under `ha:hasFilmColorType`. | KEEP. |
| The nine `dct:format` strings | Use the context-specific treatment in M03. | REVIEW; do not turn them into file-format IRIs. |

Other instance/concept IRIs remain stable unless explicitly listed above. For example, retain `/id/motivation/`, `/id/permission/`, license, rights-statement, organization-preference, carrier and file-format concept identities. Apply the class/property mappings to their descriptions where relevant, including `haRig:Motivation → ha:Motivation` on motivation concepts and renamed operands inside permission definitions. Preserve SKOS labels, definitions, scheme memberships and links on these resources. This preserves supporting vocabulary data without expanding the shape-derived class/property inventory into a full vocabulary migration audit.

## Execution plan

### 1. Record the model decisions before enabling affected rules

Assign the open role, format-classification, fragment-offset conversion and date-domain decisions to the model owner. Rights-value decisions also need the rights-model owner, and URI-template and URL decisions need application-owner input. Use actual data examples to resolve the remaining REVIEW and UNMAPPED contexts. Record the accepted destination, condition, conversion, retained provenance and validation expectation for each open context.

Identifier mappings, descriptive role names, series positions, season numbers, transcripts, coverage and both hardware and software model strings can proceed under their stated rules. Prioritize post and agent typing (M02/M13), intellectual-entity format classification (M03), unresolved fragment-offset conversions and media-file typing exceptions (M04), date domains and datatype alignment (M06), and the remaining text and caption exceptions (M07/M08).

### 2. Profile the source dataset and preserve a reproducible baseline

Freeze the source ontology/vocabulary versions and take a restorable copy or immutable source graph. Count explicit class assertions, predicates and controlled-value IRIs from this inventory. Also list observed terms outside it, because SHACL describes supported usage rather than proving which triples actually exist. Profile literal datatypes/languages, node kinds, role-wrapper patterns, identifier-system boundaries, dates, offset precision, measurement units, and cross-links to vocabulary resources.

Do not assume every source-shaped resource conforms: note existing violations separately from problems introduced by migration. Specifically check checksum creators, role agents that are generic things, variable recording speed, series-level predecessors, and public-domain values.

### 3. Apply deterministic class and predicate rules into a new graph

Use an explicit IRI map, with subject-type/context guards where specified. Preserve resource identities, blank-node structure where possible, inverse directions and relation subtypes. Apply KEEP rules as well as MAP rules so externally named data is not dropped. Apply controlled-value rewrites throughout relevant data and supporting vocabulary descriptions.

Apply the fragment class mappings and media-file typing in M04 explicitly so they are available to SHACL Core. Use the approved conversion rules for datatypes and context-specific measurement values. Deduplicate identical output triples while recording many-to-one merges. Leave source graphs unchanged and keep unresolved statements in an identifiable legacy/provenance graph.

### 4. Run the approved structural and literal conversions

Handle roles, measurements, media offsets, dates, place and country resolution, and caption models using the applicable M-rules. Reuse the existing local identifier nodes. Use deterministic identifiers for new nodes so reruns preserve their identities. Record original lexical values, language tags, predicates and conversion reasons where representation changes.

A rule that cannot establish its preconditions must produce an exception record containing the source subject, predicate, object, source graph, issue ID and reason. It must not discard the statement, fabricate precision, or silently substitute a generic value.

### 5. Validate coverage, semantics and application behavior

Write migration-specific acceptance checks from the agreed mapping decisions and source requirements. Align the draft target SHACL checks before using them for acceptance, including the local identifier paths in M01, both forms of role names in M02 and the date datatypes in M06.

| Check | Acceptance criterion |
| --- | --- |
| Inventory coverage | Every observed source class/property/value is mapped, explicitly kept, or reported as unresolved; no unclassified drops. |
| Target existence | Every emitted target class/property is declared in the model, one of its supplied imports, or an explicitly approved foundational/extension vocabulary. Flag undefined ontology references such as `ha:BibframeProductionMethod` and `ha:description` during validation. |
| Value preservation | All multilingual texts, date precision, identifier lexical forms, checksum values, measurement units and status notes survive or have an explicit loss/exception decision. |
| Context rules | Validate work and role chains, fixity attribution, and model strings on both agent types. Verify that generic generated resources and Mediahaven provenance retain their original scope. |
| Relations | Structural versus generic membership and inclusion remain distinct; inverse-copy edges remain consistent; sequence edges retain their direction. |
| Media | Source-file links connect `ha:MediaFile` and `ha:MediaFragment` in the original direction. Media files have a qualifying MIME type. Fragments preserve intellectual-entity and annotation links, and any converted offsets are integer seconds. |
| Rights | Policy targets, actions, permissions/prohibitions, constraints and motivations retain their behavior; operand IRIs/types and public-domain status patterns are correct. |
| Counts | Reconcile changes using per-rule counts. Track newly created measurement nodes, any materialized PREMIS identifier links, and merged annotation-subject triples. |
| Repeatability | Rerunning against the same frozen input produces the same graph, no duplicate generated nodes and the same exception ledger. |
| Application checks | Compare representative searches, resource displays, collection navigation, media clips, captions, request forms and rights evaluations before and after migration. |

Run checks on a sample spanning all used shapes, then the full dataset. Test both the chosen explicit-data model and any reasoning profile the applications actually use; domain/range inferences must not accidentally turn collections into intellectual works or identifier values into measurements.

### 6. Cut over only after reconciliation

Keep a mapping-version identifier, baseline counts, conversion/exception totals and validation results with the migrated graph. Update affected producers, queries, indexes and applications against the concrete crosswalk, then perform a staged read comparison. Resolve or explicitly accept remaining exceptions before retiring legacy reads. Keep the old graph available for rollback until operational checks pass; removal of old data is a separate deployment decision.

## Deliverable verification and limits

All five source shape files, the target RDFS model and its three supplied external extracts were parsed as Turtle. The crosswalk contains one entry for each of the **90 classes and 211 properties** found through active shape statements. The controlled-value crosswalk and M03 account for all **64 distinct values** from active source `sh:in` lists. Direct MAP/CHANGE/KEEP destinations were checked for declaration in the inspected target definitions, with the explicitly retained foundational RDF/SKOS terms allowed.

The 25 November revision updates the crosswalk and execution plan against the current RDFS declarations. The marked REVIEW and UNMAPPED cases identify exceptions to automatic migration. Production profiling and validation belong to the execution phase.
