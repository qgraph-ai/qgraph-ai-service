# Quran App

## Purpose

The `quran` app is the canonical scripture data layer for the backend.

It provides:

- Quran structural entities (Surah, Ayah)
- larger reading boundaries (Juz, Hizb quarter, Manzil, Ruku)
- translation source metadata
- ayah-level translation records
- read-only APIs for frontend and downstream app consumption

Other apps, especially `segmentation`, depend on this app as the source of truth for ayah and surah identity.

## Core Data Model

### Surah

Represents a chapter of the Quran, including:

- numeric order (`number`, 1..114)
- Arabic name
- transliteration/English name
- metadata such as ayah count and revelation information

### Ayah

Represents a verse with both local and global numbering:

- `number_in_surah`
- `number_global`
- canonical Arabic text
- foreign key to `Surah`

Uniqueness and indexing support both per-surah and global lookups.

### Structure Boundaries

`Juz`, `HizbQuarter`, `Manzil`, and `Ruku` models define start boundaries by referencing an ayah.

This enables consistent boundary-to-ayah range APIs.

### Translation Model

- `TranslationSource`: metadata about a translation edition/provider
- `AyahTranslation`: translation text for a specific `(ayah, source)` pair

This model supports:

- multiple translations per ayah
- filtering by language/provider/source
- optional projection of a single translation in ayah responses

## API Access Patterns

Main read flows include:

- surah list/detail + surah ayahs
- ayah list/detail + ayah translations
- ayah lookup by `(surah_number, number_in_surah)`
- search over Arabic text or translations
- structure endpoints (`juz`, `hizb-quarters`, `manzils`, `rukus`) with ayah range actions

Most list endpoints are paginated and support filtering/search/ordering where configured.

## How Other Apps Use Quran Data

Segmentation relies directly on Quran IDs:

- `SegmentationVersion` references `Surah`
- `Segment.start_ayah` / `Segment.end_ayah` reference `Ayah`
- snapshot validation checks ayah existence and surah consistency

This enforces that segmentation boundaries align with canonical Quran structure.

## Data Modeling Considerations

Current modeling decisions emphasize:

- canonical Arabic text storage in Ayah
- stable numeric identifiers for scripture-native lookups
- explicit uniqueness constraints for numbering and translation pair integrity
- provider/external ID support in translation sources for ingestion provenance

## Extensibility Notes

Likely extension areas (to document as implemented):

- richer search semantics (language-aware analyzers, ranking)
- additional metadata and indexing strategies
- expanded translation/tafsir domains
- caching strategies for high-traffic read paths

This page can be expanded with ingestion pipelines and operational playbooks as those evolve.
