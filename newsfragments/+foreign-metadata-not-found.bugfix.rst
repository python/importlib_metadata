The preference for valid distributions no longer propagates the
``MetadataNotFound`` of a distribution that a provider derived from
``importlib.metadata``, whose exception is a different class from this
package's and so escaped the preference rather than marking the distribution
invalid.
